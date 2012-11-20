(function(){

//Load Jquery
if (!($ = window.jQuery)) { // typeof jQuery=='undefined' works too  
    script = document.createElement( 'script' );  
  	script.src = 'http://ajax.googleapis.com/ajax/libs/jquery/1/jquery.min.js';  
    script.onload=runBookmarklet;  
    document.body.appendChild(script);  
}  
else {  
    runBookmarklet();  
} 



//Run Document
function runBookmarklet()
{
	selectImage();
}

function selectImage()
{
	var images = getPostableImages();
	displayImageSelector(images);
}

/*
	getPostableImages
	Returns an array of all of the images on the page
	which we deem are "good"!
*/
function getPostableImages()
{
	//TODO: Are there any other ways of getting (other types?) displayed images
	var allImages = $('img');

	//Filter Selections
	var postableImages = [];
	for(var i=0; i<allImages.length; i++)
		if(isPostableImage(allImages[i]))
			postableImages.push(allImages[i]);

	return postableImages;	
	
}

/*
	isPostableImage
	Currently the criteria is:
		width > 80px
			AND
		height > 80px 
*/
function isPostableImage(image)
{

	var MIN_WIDTH = 80;
	var MIN_HEIGHT = 80;

	return image.width > MIN_WIDTH && image.height > MIN_HEIGHT;
}

/*
	displayImageSelector
	Displays a list of the images and allows the user to choose one
*/
function displayImageSelector(images)
{
	//displayIframe();
	displayImages(images);

}

function displayIframe()
{
	//Create iframe overlay
	$('<iframe />', {
		id: "visioniFrame",
		//TODO: Get the window width and height
		width: "100%",
		height: "100%",
		frameborder: 0,
	})
	//TODO: Changed this -> absolute
	.css('position', 'fixed')
	.css('background-color', 'blue')
	.css('top', 0)
	.css('left', 0)
	.css('right', 0)
	.css('bottom', 0)
	.css('z-index', 2147483642)
	.appendTo('body');
	//iframe.allowTransparency = "true"
}

function displayImages(images)
{
	var backgroundDiv = addBackground();
	for(var i=0; i < images.length; i++)
		showImage(images[i], i, backgroundDiv);
}

function addBackground()
{
	return $("<div />", {
		//TODO: add radom numbers to the css selectors (id)
		id: "VISION_SELECTOR_BACKGROUND",
		width: "2000px",
		height: "2000px"
	})
	//TODO: Change to absolute
	.css('position', 'fixed')
	.css('top', 0)
	.css('left', 0)
	.css('right', 0)
	.css('bottom', 0)
	.css('background-color', '#F2F2F2')
	.css('opacity', .95)
	.css('z-index', 2147483643)
	.css('padding-left', '10%')
	.css('padding-right', '10%')
	.appendTo('body');

}

function showImage(image, index, background)
{
	//Pinterest Minimum Image Size
	//> 80px in both dimensions
	THUMBNAIL_HEIGHT = 200;
	THUMBNAIL_WIDTH = 200;

	$('<img />', {
		class: "VISION_SELECTOR_IMAGE",
		height: THUMBNAIL_HEIGHT,
		width: THUMBNAIL_WIDTH,
		src: image.src
	})
	.css('margin-left', '20px')
	.css('margin-right', '20px')
	.css('opacity', 1)
	.css('cursor', 'pointer')
	.hover(
		function(){
			$(this).css('opacity', .95);
			$(this).css('background-color', "#333");
		}, 
		function() {
			$(this).css('opacity', 1);
		}
	)
	//Post Image
	.click(function(){

		var mediaUrl = image.src;

		var pageUrl = window.location.href;
		var pageTitle = document.title;

		//Media description is 1st alt tag and if no alt tag, 2nd page title, 
		//e(can make it more detailed when we imporve the description finding)
		var mediaDescription; 
		image.alt == "" ? mediaDescription = pageTitle
			: mediaDescription = image.alt;

		//Debug
		/*
		console.log("Media Url: " + mediaUrl);
		console.log("Page Url:" + pageUrl);
		console.log("Page Title: " + pageTitle);
		console.log(image);
		console.log(image.alt);
		console.log("Media Description: " + mediaDescription);
		*/

		saveVision(mediaUrl, mediaDescription, pageUrl, pageTitle);
	})
	//.css('float', 'left')
	.appendTo(background);
}

function saveVision(mediaUrl, mediaDescription, pageUrl, pageTitle)
{

	/*
		Saved by pinterest
		(passed in the url)

		Media URL
		media=http%3A%2F%2Fmollypiper.com%2Fwp-content%2Fuploads%2F2011%2F02%2Fzoolander.jpg

		Page Url
		url=http%3A%2F%2F127.0.0.1%3A5000%2F
	
		Page Title
		&title=Project%20AWESOME
		is_video=false

		This is the image alt tag
		Defaults to page title if there is no alt tag
		description=Project%20AWESOME
	*/

	var BASE_URL = "http://127.0.0.1:5000/vision/create/bookmarklet";
	var MEDIA_URL_KEY = "mediaUrl";
	var PAGE_URL_KEY = "pageUrl";
	var PAGE_TITLE_KEY = "pageTitle";
	var MEDIA_DESCRIPTION_KEY = "mediaDescription";

	var url = BASE_URL;
 	url += "?" + getQueryComponent(MEDIA_URL_KEY, mediaUrl);
	url += "&" + getQueryComponent(PAGE_URL_KEY, pageUrl);
	url += "&" + getQueryComponent(PAGE_TITLE_KEY, pageTitle);
	url += "&" + getQueryComponent(MEDIA_DESCRIPTION_KEY, mediaDescription)
	
	var name = "Create Vision";
	//From Pinterest Specs
	var specs = "status=no,resizable=yes,scrollbars=yes,personalbar=no,directories=no,location=no,toolbar=no,menubar=no,width=632,height=270,left=0,top=0";
	
	window.open(url, name, specs);
}

/*
	Get Query Component
	Encode Query Url
*/
function getQueryComponent(key, value)
{
	return key + '=' + encodeURIComponent(value);
}


function saveVisionAjax(imageUrl) {  

	var url = "http://127.0.0.1:5000/save";
	console.log(window.location);
	//Test
	$.ajax({
		url:url,
		dataType: 'jsonp',
		data: {
			url: window.location.href,
			text: window.location.origin,
			img: imageUrl
		},
		success: function(data){
			alert(data);
			console.log(data);
		}
	});
}  

})();
