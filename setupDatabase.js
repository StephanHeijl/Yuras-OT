/* 
 * Create Database MongoDB/TokuMX
 * It will set up some indexes to allow expiring data after a certain period of time.
 */

print("Configuring MongoDB for Yuras Operations");
print("========================================");
print("");

conn = new Mongo();

rs.initiate({
        "_id" : "rs0",
        "members" : [
                {
                        "_id" : 0,
                        "host" : "vagrant-ubuntu-trusty-64:27017",
                        "arbiterOnly" : false,
                        "buildIndexes" : true,
                        "hidden" : false,
                        "priority" : 1,
                        "tags" : {

                        },
                        "slaveDelay" : 0,
                        "votes" : 1
                },
                {
                        "_id" : 1,
                        "host" : "vagrant-ubuntu-trusty-64:27018",
                        "arbiterOnly" : false,
                        "buildIndexes" : true,
                        "hidden" : false,
                        "priority" : 0.5,
                        "tags" : {

                        },
                        "slaveDelay" : 0,
                        "votes" : 1
                }
        ],
        "settings" : {
                "chainingAllowed" : true,
                "heartbeatTimeoutSecs" : 10,
                "getLastErrorModes" : {

                },
                "getLastErrorDefaults" : {
                        "w" : 1,
                        "wtimeout" : 0
                }
        }
})

print("* Connected.");
db = conn.getDB(database);
print("* Selected Client Database.");
db.documents.ensureIndex( { "tags" : 1 } );
print("* Ensured index on tags.");

print("\nAll done.\n");