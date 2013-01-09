/*
	Postmarklet

	1/8/2013
	TODO:
		1. Handle this page: http://twitter.github.com/bootstrap/base-css.html
		2. Proportion Thumbnails
		3. Minify js & css
*/


if (typeof __PROJECT_AWESOME_DEBUG__ == 'undefined') {
	console.log('debug is not defined, using production!');
    __PROJECT_AWESOME_DEBUG__ = false;
}

(function(){

//Choose the correct domain
//TODO: Decide if we want to switch this to a query parameter
if (__PROJECT_AWESOME_DEBUG__ == true) {
    DOMAIN_BASE_URL = "http://127.0.0.1:5000";
    STATIC_BASE_URL = DOMAIN_BASE_URL + "/static";
    console.log("In Local Version");
} else {
    DOMAIN_BASE_URL = "http://project-awesome.herokuapp.com";
    STATIC_BASE_URL = "https://s3.amazonaws.com/project-awesome-static/gen";
    console.log("In Production Version");
}

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
	loadCSS();
	var images = getPostableImages();

	//Make sure we have at least 1 good image
	if(images.length == 0)
		alert("Sorry, we couldn't find any postable images on this page!");
	else
		displayImageSelector(images);
}

//Load the CSS file for the images
function loadCSS()
{
  var CSS_FILE_URL = STATIC_BASE_URL + "/css/postmarklet.css";
 
  var cssLink =document.createElement("link")
  cssLink.setAttribute("rel", "stylesheet")
  cssLink.setAttribute("type", "text/css")
  cssLink.setAttribute("href", CSS_FILE_URL)
  document.getElementsByTagName("head")[0].appendChild(cssLink)
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
	// What to append to
	var BASE = 'body';

	//displayIframe();
	displayBackground(BASE);
	var body = displayBody(BASE);
	displaySpacer(body);
	displayHeader(body);
	displayImages(body, images);

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


//TODO: add radom numbers to the css selectors (id)
function displayBackground(baseElement)
{
	$("<div />", {
		id: "CREATE_VISION_BACKGROUND",
	})
	.appendTo(baseElement);

}

function displayBody(baseElement)
{
	return $("<div />", {id: "CREATE_VISION_BODY"})
			.appendTo(baseElement);
}


function displaySpacer(body)
{
	$("<div />", {id: "CREATE_VISION_SPACER"})
	.appendTo(body);
}

function displayHeader(body)
{
	var headerDiv = $("<div />", {id:"CREATE_VISION_HEADER"})
				.appendTo(body);


	//Logo
	$("<span />", {
		id: "CREATE_VISION_LOGO",
		text: "Project Awesome"
	}).appendTo(headerDiv);

	//Cancel
	$("<a />", {
		id: "CREATE_VISION_X",
		text: "Cancel",
		click: cancelClicked
	}).appendTo(headerDiv);
}



function displayImages(visionBodyDiv, images)
{
	var imageContainer = $("<span />", {id: "CREATE_VISION_IMAGE_CONTAINER"})
							.appendTo(visionBodyDiv);

	for(var i=0; i < images.length; i++)
		showImage(images[i], i, imageContainer);
}

function showImage(image, index, imageContainer)
{
	var visionContainer = $('<span />', {
		class: "CREATE_VISION_VISION_CONTAINER"
	}).appendTo(imageContainer);

	var imageSpan = $('<span />', {
		class: "CREATE_VISION_IMAGE"
	}).appendTo(visionContainer);

	//Pinterest Minimum Image Size
	//> 80px in both dimensions
	THUMBNAIL_HEIGHT = 200;
	THUMBNAIL_WIDTH = 200;

	//Thumbnail Image
	$('<img />', {
		height: THUMBNAIL_HEIGHT,
		width: THUMBNAIL_WIDTH,
		src: image.src
	}).appendTo(imageSpan);

	$('<a />', {
		rel: "image",
		href: "#"
	})
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
	.appendTo(imageSpan);
}


/*
	------------------------ Click Handlers ------------------------
*/

/*
	Cancel Clicked
*/
function cancelClicked()
{
	//Remove background and body
	$('#CREATE_VISION_BACKGROUND').remove();
	$('#CREATE_VISION_BODY').remove();
}
	
/*
	Image Clicked
*/
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

	var BASE_URL = DOMAIN_BASE_URL + "/vision/create/bookmarklet";
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

/*
function saveVisionAjax(imageUrl) {  

	var url = DOMAIN_BASE_URL + "/save";
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
*/

})();
