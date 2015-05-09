conn = new Mongo();
db = conn.getDB("Yuras1");
var cursor = db.documents.find();
while (cursor.hasNext()) {
  var x = cursor.next();
  print("Before: "+x['judicial_instance']);
  try {
	  x['judicial_instance'] = x['judicial_instance'].replace(' ', '_');
  } catch(err) {
  	print("No judicial instance")
  }
  print("After: "+x['judicial_instance']);
  db.documents.update({_id : x._id}, x);
}
