var s = new sigma('graph-background');
s.settings({
	mouseWheelEnabled: false,
	mouseEnabled: false,
	touchEnabled: false,
	minNodeSize:2,
	maxNodeSize:8
});
var n = 35;
// Then, let's add some data to display:
for( i=0; i<n; i++) {
	s.graph.addNode({
	  // Main attributes:
	  id: 'n'+i,
	  // Display attributes:
	  x: Math.random()*100,
	  y:  Math.random()*100,
	  size: Math.random(),
	  color: 'black'
	})
}

for( i=0; i<n; i++ ) {
	for( e=0; e<3; e++ ) {
		s.graph.addEdge({
			id:("e"+i)+e,
			source:"n"+i,
			target:"n"+parseInt(Math.random()*n)
		})
	}
}

s.refresh();
s.startForceAtlas2({
	slowDown:500,
	linLogMode:true,
	gravity:0.3
})

setTimeout(function() {
	s.stopForceAtlas2()
}, 60000);