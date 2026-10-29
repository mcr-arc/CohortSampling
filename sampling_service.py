import pandas as pd
from typing import Dict, Any, List
from deterministic_filtering import FetchData
from filter_parser import FilterParser


class SamplingAIService:
    def __init__(self, data_path: str):
        self.fetcher = FetchData(data_path)
        self.df = self.fetcher.df.copy()
        self.parser = FilterParser()

    def get_valid_columns(self) -> List[str]:
        """
        Restrict AI to columns researchers are allowed to filter on.
        """
        allowed_filter_columns = ["DxDate", "Race1", "DxCounty", "AgeGroup", "SiteGroup", "Recode", "AgeDx", "HistTypeICDO3", "PSite"]
        return [col for col in allowed_filter_columns if col in self.df.columns]


    def normalize_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match AI output values to dataframe types.
        """
        normalized = {}

        
        for key, val in filters.items():
            if not val:
                continue
            
            if key not in self.df.columns:
                continue

            if key == "DxDate":
                if isinstance(val, list):
                    normalized[key] = [str(v) for v in val]
                else:
                    normalized[key] = str(val)

            elif key in ["DxCounty", "Race1"]:
                if isinstance(val, list):
                    normalized[key] = [int(v) for v in val]
                else:
                    normalized[key] = int(val)

            elif key == "Recode":
                if isinstance(val, list):
                    normalized[key] = [int(v) for v in val]
                else:
                    normalized[key] = int(val)
            
            elif key in ["RespHosp", "Phone"]:
                if isinstance(val, list):
                    normalized[key] = [str(int(float(v))) for v in val]
                else:
                    normalized[key] = str(int(float(val)))

            else:
                if isinstance(val, list):
                    normalized[key] = [str(v) for v in val]
                else:
                    normalized[key] = str(val)

        return normalized

    def validate_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Checks whether AI-generated filters are valid.
        """
        valid_columns = self.get_valid_columns()
        errors = []
        warnings = []

        for col, val in filters.items():
            if not val:
                continue
            if col not in valid_columns:
                print(col)
                errors.append(f"Invalid filter column: {col}")
                continue

            available_values = set(self.df[col].dropna().astype(str).unique().tolist())

            requested_values = val if isinstance(val, list) else [val]

            for requested in requested_values:
                if str(requested) not in available_values:
                    warnings.append(f"Value '{requested}' was not found in column '{col}'.")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    def apply_filters_preview(self, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Applies filters without sampling, so we can check feasibility first.
        """
        temp_df = self.df.copy()

        if "Phone" in temp_df.columns:
            temp_df = temp_df[temp_df["Phone"].notna()]

        for col, val in filters.items():
            if col not in temp_df.columns:
                continue

            if isinstance(val, list):
                temp_df = temp_df[temp_df[col].isin(val)]
            else:
                temp_df = temp_df[temp_df[col] == val]

        return temp_df

    def suggest_widening(self,filters: Dict[str, Any],matched_count: int,requested_n: int) -> List[str]:
        """
        Simple rule-based widening suggestions.
        """
        suggestions = []

        if matched_count == 0:
            suggestions.append("Remove one or more filters and try again.")

        if "DxDate" in filters:
            suggestions.append("Widen the diagnosis year range.")

        if "AgeGroup" in filters:
            suggestions.append("Include adjacent age groups.")

        if "DxCounty" in filters:
            suggestions.append("Include nearby or additional counties.")

        if matched_count < requested_n:
            suggestions.append(f"Reduce the requested sample size from {requested_n} to {matched_count}.")

        if "Race1" in filters:
            suggestions.append("Review whether the race filter is too restrictive.")

        return suggestions

    def run_researcher_request(self, user_query: str) -> Dict[str, Any]:
        """
        End-to-end:
        natural language -> JSON -> validate -> feasibility -> sample or suggest widening.
        """

        parsed_request = self.parser.parse_request(user_query=user_query, valid_columns=self.get_valid_columns(),)

        n = parsed_request.n
        filters = self.normalize_filters(parsed_request.model_dump().get('filters'))
        print("First filrers: ",filters)
        validation = self.validate_filters(filters)

        if not validation["is_valid"]:
            return {
                "status": "invalid_filters",
                "message": "The request contains invalid filter fields.",
                "parsed_request": parsed_request.model_dump(),
                "errors": validation["errors"],
                "warnings": validation["warnings"]
            }

        preview_df = self.apply_filters_preview(filters)
        matched_count = len(preview_df)

        if matched_count == 0:
            return {
                "status": "no_matches",
                "message": "No records matched the requested filters.",
                "parsed_request": parsed_request.model_dump(),
                "filters": filters,
                "matched_count": matched_count,
                "warnings": validation["warnings"],
                "suggestions": self.suggest_widening(filters, matched_count, n)
            }

        if matched_count < n:
            return {
                "status": "insufficient_matches",
                "message": f"Only {matched_count} eligible records matched, but {n} were requested.",
                "parsed_request": parsed_request.model_dump(),
                "filters": filters,
                "matched_count": matched_count,
                "requested_n": n,
                "warnings": validation["warnings"],
                "suggestions": self.suggest_widening(filters, matched_count, n)
            }

        sampled_df = self.fetcher.get_stratified_sample(n=n, filters=filters)

        if sampled_df is None or len(sampled_df) == 0:
            return {
                "status": "sampling_failed",
                "message": "Filters matched records, but sampling failed.",
                "parsed_request": parsed_request.model_dump(),
                "filters": filters
            }

        return {
            "status": "success",
            "message": f"Successfully generated sample of {len(sampled_df)} records.",
            "parsed_request": parsed_request.model_dump(),
            "filters": filters,
            "matched_count": matched_count,
            "sample_size": len(sampled_df),
            "sample": sampled_df
        }