$(function() {
	if( $(".generate-password").length > 0 ) {
		generatePassword = function() {
			inputs = $(".generate-password").find("input")
			N = inputs.length
			$.getJSON("/users/get-random-words/"+N, function( words ) {
				$.each(	words, function(w, word) {
					inputs.eq(w).val(word);	
				});
			})
		};
		
		$(".generate-new-password").click(generatePassword)
		generatePassword()
	}
});