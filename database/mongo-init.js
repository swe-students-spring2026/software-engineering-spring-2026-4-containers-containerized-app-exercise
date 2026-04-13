db = db.getSiblingDB("birdnet_db");

db.createCollection("recordings");
db.createCollection("detections");

db.recordings.createIndex({ recorded_at: -1 });
db.detections.createIndex({ recording_id: 1 });
db.detections.createIndex({ species_name: 1 });
db.detections.createIndex({ confidence: -1 });