"""
This file contain the functions to connect to google analytics data api
"""
import re
from typing import List, Optional, Dict, Iterable


def run_report(
        property_id: str,
        dimensions: List[str],
        metrics: List[str],
        start_date: str,
        end_date: Optional[str]) -> 'RunReportResponse':
    """
    Run report on GA4 property with given dimension and metrics

    :param property_id: The identity of the GA property
    :param dimensions: A list of dimension names
    :param metrics: A list of metric ids
    :param start_date: Start date to run the report from
    :param end_date: End date to run the report till
    :return: values matrix
    """

    from google.analytics.data import (
        BetaAnalyticsDataClient,
        RunReportResponse, RunReportRequest, Dimension, Metric, DateRange
    )

    client = BetaAnalyticsDataClient()

    request = RunReportRequest(
        property=f"properties/{property_id}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date or "today")])

    return client.run_report(request)


def check_configuration(config: Dict[str, str]):
    assert "prefix" in config, "No prefix given, need one to decide table name"
    assert "property_id" in config, "No property ID provided"
    assert "metrics" in config, "No metrics given"
    assert "dimensions" in config, "No dimensions given"

    # Validate prefix
    prefix = config["prefix"]
    assert prefix and len(prefix) > 3, "Prefix should have at-least 3 characters"
    prefix_pat = re.compile("[a-z][a-z0-9_]+")
    assert prefix_pat.match(prefix), (
        "Prefix should start with a lower-case letter and contain lower-case alphanumeric characters and underscore"
    )

    # Validate property ID
    property_id = config["property_id"]
    assert len(property_id) > 6, "Property ID is too short"
    property_id_pat = re.compile(r"""\w{1,2}-\w+-\w+""")
    assert property_id_pat.match(property_id), (
        "Invalid property ID. Should be in [GA VERSION]-[client id]-[property index] format."
    )

    # Validate dimensions
    dimensions = [d.strip() for d in config["dimensions"].split(",")]
    assert dimensions, "You need at-least one dimension"
    assert len(dimensions) <= 9, "Too many dimensions specified, you can have up-to 9 dimensions."

    # Validate metrics
    metrics = [d.strip() for d in config["metrics"].split(",")]
    assert metrics, "You need at-lease one metric"
    assert len(metrics) <= 10, "Too many metrics, you can have up-to 10 metrics."

    from google.analytics.data import BetaAnalyticsDataClient, CheckCompatibilityRequest

    try:
        client = BetaAnalyticsDataClient()
        request = CheckCompatibilityRequest(mapping={
            "property": f"property/{property_id}",
            "dimensions": config["dimensions"].split(", "),
            "metrics": config["metrics"].split(", ")
        })
        response = client.check_compatibility(request)
        # TODO: check response for incompatibilities
    except AssertionError as e:
        raise e
    except Exception as e:
        raise AssertionError("Cannot connect to google analytics service", e)


def extract_rows(config: Dict[str, str], response: 'RunReportResponse') -> Iterable[Dict[str, str]]:
    """
    Extract data rows from a run report result

    :param config: Configuration dictionary
    :param response: Response of run report endpoint

    :result: A generator which will yield data dictionaries per row
    """
    dim_len = len(response.dimension_headers)
    metric_len = len(response.metric_headers)
    for row in response.rows:
        row_data = {}
        for i in range(0, dim_len):
            row_data.update({response.dimension_headers[i].name: row.dimension_values[i].value})
        for i in range(0, metric_len):
            row_data.update({response.metric_headers[i].name: row.metric_values[i].value})
        yield row_data
