
$(document).ready(function() {
//
//  $('[data-toggle="offcanvas"]').click(function() {
//    $('#wrapper').toggleClass('toggled');
//  });
//
//  // Toggle the class
//  $('body').on('click', '.dropdown', function() {
//    $(this).toggleClass('show');
//  });

	// DOMContentLoaded  end

   $('.quantite-right-plus').click(function(e){
        // Stop acting like a button
        e.preventDefault();
        // Get the field name
        var quantite = parseFloat($('#quantite').val());
        
        // If is not undefined
            $('#quantite').val(quantite + 1);  // Increment
        
    });

     $('.quantite-left-minus').click(function(e){
        // Stop acting like a button
        e.preventDefault();
        // Get the field name
        var quantite = parseFloat($('#quantite').val());

            if(quantite>1){
             $('#quantite').val(quantite - 1);
            }
    });


   $('.bouton_recherche').click(function(e){
        // Stop acting like a button
        // e.preventDefault();
        var recherche = $('#recherche').val();
        location.href="/search/?"+recherche;

    });
});

document.onreadystatechange = function() {
    if (document.readyState == "complete") {
        $("#loader").css('display', "none");
        /*$("#contenucharge").css('visibility', "visible");*/
    } else {
        /*$("#contenucharge").css('visibility', "hidden");*/
        $("#loader").css('visibility', "visible");
    }
};
/*

document.addEventListener("DOMContentLoaded", function(){

		navbar = $('#navbar')

		// add padding-top to bady (if necessary)
		//navbar_height = document.querySelector('.navbar').offsetHeight;
		//document.body.style.paddingTop = navbar_height + 'px';

		if(navbar){
			var last_scroll_top = 0;
			window.addEventListener('scroll', function() {
	       		let scroll_top = window.scrollY;
		       if(scroll_top < last_scroll_top) {
		            navbar.removeClass('scrolled-down');
		            navbar.addClass('scrolled-up');
		        }
		        else {
		            navbar.removeClass('scrolled-up');
		            navbar.addClass('scrolled-down');
		        }
		        last_scroll_top = scroll_top;
			});
			// window.addEventListener

		}
		// if

	});
*/
(function(){
    $('bouton_rechercher').click(function(e) {
        var recherche = $('#recherche').val();
        location.href="/search/?"+recherche;
    });

    if ($('#scroll-to-top').length) {
		var scrollTrigger = 100, // px
			backToTop = function () {
				var scrollTop = $(window).scrollTop();
				if (scrollTop > scrollTrigger) {
					$('#scroll-to-top').addClass('show');
				} else {
					$('#scroll-to-top').removeClass('show');
				}
			};
		backToTop();
		$(window).on('scroll', function () {
			backToTop();
		});
		$('#scroll-to-top').on('click', function (e) {
			e.preventDefault();
			$('html,body').animate({
				scrollTop: 0
			}, 700);
		});
	}
})
//$(function() {
//   $('button').click(function() {
//        var quantite = parseInt($('#quantite').val());
//        location.href="/panier/ajouter"
//   });
//});
//$(function() {
//   $('buttonAjouterAuPanier').click(function() {
//        var quantite = parseFloat($('#quantite').val());
//        location.href="/panier/ajouter"
//   });
//});


function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
      console.log('Async: Copying to clipboard was successful!');
    }, function(err) {
      console.error('Async: Could not copy text: ', err);
    });
}

function copyToClipboardElement(element) {
    navigator.clipboard.writeText($(element).text()).then(function() {
      console.log('Async: Copying to clipboard was successful!');
    }, function(err) {
      console.error('Async: Could not copy text: ', err);
    });
}

function toggle_visibility(id) {
   var e = document.getElementById(id);
   if(e.style.display == 'inline'){
      e.style.display = 'none';
  }else{
      e.style.display = 'inline';
  }
}

function scrollToMe(element) {
    location.href = element;
}

function geoFindMe() {
  const status = document.querySelector("#status");
  const mapLink = document.querySelector("#map-link");

  mapLink.href = "";
  mapLink.textContent = "";

  function success(position) {
    const latitude = position.coords.latitude;
    const longitude = position.coords.longitude;

    status.textContent = "";
    mapLink.href = `https://www.openstreetmap.org/#map=18/${latitude}/${longitude}`;
    mapLink.textContent = `Latitude: ${latitude} °, Longitude: ${longitude} °`;
  }

  function error() {
    status.textContent = "Impossible de retrouver votre position";
  }

  if (!navigator.geolocation) {
    status.textContent = "Geolocalisation indisponible dans votre navigateur";
  } else {
    status.textContent = "Locating…";
    navigator.geolocation.getCurrentPosition(success, error);
  }
}


/* document.querySelector("#find-me").addEventListener("click", geoFindMe);*/
