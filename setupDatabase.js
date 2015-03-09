/* 
 * Create Database MongoDB/TokuMX
 * It will set up some indexes to allow expiring data after a certain period of time.
 */

print("Configuring MongoDB for Yuras Operations");
print("========================================");
print("");

conn = new Mongo();
print("* Connected.");
db = conn.getDB(database);
print("* Selected Client Database.");
db.documents.ensureIndex( { "tags" : 1 } );
print("* Ensured index on tags.");
db.documents.createIndex( { contents: "text" } )
print("* Ensured text index on contents.");

print("\nAll done.\n");