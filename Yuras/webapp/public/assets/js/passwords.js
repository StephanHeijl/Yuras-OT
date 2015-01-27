$(function () {
		retrievePasswords = function (n) {
			words = new $.Deferred();
			$.getJSON("/users/get-random-words/" + n, function (data) {
				words.resolve(data);
			});

			return words.promise()
		}

		setPasswords = function (passwords) {
			for (pw in passwords) {
				$("#password-preview input").eq(pw).val(passwords[pw])
			}
		}

		refreshPasswords = function () {
			$.when(retrievePasswords(4)).then(
				function (passwords) {
					setPasswords(passwords)
				}
			)
		};

		refreshPasswords();
		
		$("#refresh-password").click(refreshPasswords)
});