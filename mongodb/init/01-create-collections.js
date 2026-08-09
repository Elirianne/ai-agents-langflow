// Creates the time-series collections used by the perf_metrics database.
// Runs automatically on first container start (docker-entrypoint-initdb.d),
// before 02-import-seed-data.sh loads the static seed documents.

db.createCollection("api_performance_metrics", {
  timeseries: {
    timeField: "date",
    metaField: "meta",
    granularity: "hours",
  },
});

// NOTE: Disabled for now
// db.createCollection("infra_metrics", {
//   timeseries: {
//     timeField: "timestamp",
//     metaField: "meta",
//     granularity: "minutes",
//   },
// });

db.api_performance_metrics.createIndex({ "meta.endpoint": 1, date: 1 });
// db.infra_metrics.createIndex({ "meta.host": 1, timestamp: 1 });

print("Created time-series collections: api_performance_metrics");
