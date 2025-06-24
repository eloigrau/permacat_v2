
$(document).ready(function() {
   $('.quantite-right-plus').click(function(e){
        e.preventDefault();
        var quantite = parseFloat($('#quantite').val());
            $('#quantite').val(quantite + 1);
    });

     $('.quantite-left-minus').click(function(e){
        e.preventDefault();
        var quantite = parseFloat($('#quantite').val());
            if(quantite>1){
             $('#quantite').val(quantite - 1);
            }
    });

   $('.bouton_recherche').click(function(e){
        var recherche = $('#recherche').val();
        location.href="/search/?"+recherche;
    });

fetchNotifications();
setInterval(fetchNotifications, 60000);
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
$( function()
{
    var targets = $( '[rel~=tooltip]' ),
        target  = false,
        tooltip = false,
        title   = false;

    targets.bind( 'mouseenter', function()
    {
        target  = $( this );
        tip     = target.attr( 'title' );
        tooltip = $( '<div id="tooltip"></div>' );

        if( !tip || tip == '' )
            return false;

        target.removeAttr( 'title' );
        tooltip.css( 'opacity', 0 )
               .html( tip )
               .appendTo( 'body' );

        var init_tooltip = function()
        {
            if( $( window ).width() < tooltip.outerWidth() * 1.5 )
                tooltip.css( 'max-width', $( window ).width() / 2 );
            else
                tooltip.css( 'max-width', 340 );

            var pos_left = target.offset().left + ( target.outerWidth() / 2 ) - ( tooltip.outerWidth() / 2 ),
                pos_top  = target.offset().top - tooltip.outerHeight() - 20;

            if( pos_left < 0 )
            {
                pos_left = target.offset().left + target.outerWidth() / 2 - 20;
                tooltip.addClass( 'left' );
            }
            else
                tooltip.removeClass( 'left' );

            if( pos_left + tooltip.outerWidth() > $( window ).width() )
            {
                pos_left = target.offset().left - tooltip.outerWidth() + target.outerWidth() / 2 + 20;
                tooltip.addClass( 'right' );
            }
            else
                tooltip.removeClass( 'right' );

            if( pos_top < 0 )
            {
                var pos_top  = target.offset().top + target.outerHeight();
                tooltip.addClass( 'top' );
            }
            else
                tooltip.removeClass( 'top' );

            tooltip.css( { left: pos_left, top: pos_top } )
                   .animate( { top: '+=10', opacity: 1 }, 50 );
        };

        init_tooltip();
        $( window ).resize( init_tooltip );

        var remove_tooltip = function()
        {
            tooltip.animate( { top: '-=10', opacity: 0 }, 50, function()
            {
                $( this ).remove();
            });

            target.attr( 'title', tip );
        };

        target.bind( 'mouseleave', remove_tooltip );
        tooltip.bind( 'click', remove_tooltip );
    });
});


function fetchNotifications() {
    fetch('/ajax/nbmessages/')
        .then(response => response.json())
        .then(data => {
            if (data.nb_messages > 0) {
                document.getElementById('nbmessage-badge')
                    .innerText = data.nb_messages;
                document.getElementById('nbmessage-badge')
                    .style.display = 'inline-block';
            } else {
                document.getElementById('nbmessage-badge')
                    .style.display = 'none';
            }
        })
        .catch(error => console.error('Erreur lors de la récupération des notifications:', error));
}