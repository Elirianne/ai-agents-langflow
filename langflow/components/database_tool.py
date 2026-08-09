# from lfx.field_typing import Data
import os
from pymongo import MongoClient
from datetime import datetime, timedelta, timezone

from lfx.custom.custom_component.component import Component
from lfx.io import MessageTextInput, Output
from lfx.schema.data import Data

class DatabaseTool(Component):
    display_name = "MongoDB Perf Metrics Search Tool"
    description = (
        "Fetch API performance metrics (one entry per day per endpoint) for "
        "the last N days from MongoDB."
    )
    icon = "database"
    name = "DatabaseTool"

    inputs = [
        MessageTextInput(
            name="days",
            display_name="Number of last days",
            info="How many days back to include, e.g. 7 for 'last week'. Data only covers the last 30 days.",
            value="30",
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Output", name="output", method="run_query"),
    ]

    def run_query(self) -> Data:
        #  Connect to MongoDB 
        client = MongoClient(os.environ["MONGODB_CONNECTION_STRING"])
        db = client.get_default_database()

        days = int(self.days) if self.days else 30
        since = datetime.now(timezone.utc) - timedelta(days=days)
        docs = list(
           db.api_performance_metrics.find({"date": {"$gte": since}}, {"_id": 0}).sort("date", -1)
        )
        
        # Disconnect form MongoDB
        client.close()
        
        # Return results
        return Data(data={"results": docs})
