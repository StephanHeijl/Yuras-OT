chrome.app.runtime.onLaunched.addListener(function () {
	chrome.app.window.create('container.html', {
		'bounds': {
			'width': 1280,
			'height': 800
		},
		'frame': {
			'type': 'chrome'
		}
	});
});