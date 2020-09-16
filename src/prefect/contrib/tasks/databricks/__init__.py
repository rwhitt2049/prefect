"""
This module contains a collection of tasks for interacting with Databricks resources.
"""

from prefect.contrib.tasks.databricks.databricks_submitjob import DatabricksSubmitRun
from prefect.contrib.tasks.databricks.databricks_submitjob import DatabricksRunNow

import warnings

warnings.warn(
    "Importing from `prefct.contrib.tasks` has been deprecated and instead should be `prefect.tasks`"
)
