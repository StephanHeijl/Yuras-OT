doc = undefined;
elementHeight = undefined;
bodyHeight = undefined;

$(function() {

    $("link[rel=stylesheet-sass]").each(function() {

        var documentUrl = $(this).attr("href");
        $.get(documentUrl, function(scss) {
            css = Sass.compile(scss);
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

			console.log(bodyHeight, elementHeight, bodyHeight+elementHeight, 1100*0.6, $(this));

			if(bodyHeight + elementHeight >= doc.innerHeight() - parseInt(doc.find(".document-content-padding").css("padding-top"))*2) {

				children = $(this).children();
				if(children.length > 1) {
					addToPages(children);
					return;
				}

				console.log("Creating a new page.")
				doc.appendTo($(".wrapper"));
				doc = $(".document").eq(0).clone();
				doc.find(".document-body").html("");
				doc.appendTo($(".wrapper"));

			}
			$(this).appendTo(doc.find(".document-body"));
		});
	}

	setTimeout( function() {
		doc = $(".document").eq(0).clone();
		doc.find(".document-body").html("");
		doc.appendTo($(".wrapper"));
		addToPages( $(".document-body").first().children() );
		$(".document").eq(0).remove();
	}, 1000)

});
