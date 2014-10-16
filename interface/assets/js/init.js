doc = undefined;
elementHeight = undefined;
bodyHeight = undefined;

currentPage = 0;

$(function() {

    $("link[rel=stylesheet-sass]").each(function() {

        var documentUrl = $(this).attr("href");
        $.get(documentUrl, function(scss) {
            css = Sass.compile(scss);
			console.log(css);
            $("body").append("<style>"+css+"</style>");
        });

    });

    $(".markdown").each(function() {
        md = $(this).text();
        $(this).html( markdown.toHTML(md) );
    });
});

$(function() {

	/* Divide content over pages. */

	addToPages = function(elements) {
		elements.each(function() {
			bodyHeight = parseInt(doc.find(".document-body").css("height"));
			elementHeight = parseInt($(this).outerHeight(true));

			if(bodyHeight + elementHeight >= doc.innerHeight() - parseInt(doc.find(".document-content-padding").css("padding-top"))*2) {

				children = $(this).children();
				if(children.length > 1) {
					addToPages(children);
					return;
				}

				doc.appendTo($(".wrapper"));
				doc = $(".document").eq(0).clone();
				doc.find(".document-body").html("");
				doc.appendTo($(".document-wrapper"));

			}
			$(this).appendTo(doc.find(".document-body"));
		});
	}

	setTimeout( function() {
		doc = $(".document").eq(0).clone();
		doc.find(".document-body").html("");
		doc.appendTo($(".document-wrapper"));
		addToPages( $(".document-body").first().children() );
		$(".document").eq(0).remove();
	}, 1000)

	/* Handle switching the annotation page */
	$(window).on("scroll", function() {
		var st = $("body").scrollTop();
		tmpCurrentPage = -1;
		$(".document").each(function() {
			var distance = st - $(this).offset().top;
			if( distance > 0 ) {
				tmpCurrentPage++;
			}
		});

		tmpCurrentPage = (tmpCurrentPage<0)?0:tmpCurrentPage;

		if( tmpCurrentPage != currentPage) {
			currentPage = tmpCurrentPage;
			console.log("Switched page")
			var annotationPages = $(".annotation-page");

			if( annotationPages.length <= currentPage) {
				return false;
			}

			console.log( " Annotations available. ")
			var annotationPage = $(".annotation-page").eq(currentPage);
			var paddingTop = parseInt($(".annotation-wrapper-padding").css("padding-top"));

			$(".annotation-wrapper").animate({scrollTop: annotationPage.position().top - paddingTop}, 500);

		}

	});

});
