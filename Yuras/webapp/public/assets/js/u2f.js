$(function () {
	$("#enrollU2F").click(function () {
		id = $(this).data("user-id");

		window.u2f.register([
			{
				version: "U2F_V2",
				challenge: "YXJlIHlvdSBib3JlZD8gOy0p",
				appId: "http://example.org",
				sessionId: "26"
    }
], [], function (data) {
			console.log(data);
		});


		$.getJSON("/users/" + id + "/u2f/enroll", function (data) {
			registerRequests = data["registerRequests"][0]
			window.u2f.register([registerRequests], [], function (data) {
				console.log(data);
			});
		});


	});
})