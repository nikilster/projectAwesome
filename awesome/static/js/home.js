/******************************************************************************
 * home.js
 *
 * Implements JS for main vision board view
 ******************************************************************************/

/*
    Debug
*/
var DEBUG = false;

//Onboarding
var ONBOARDING_MODAL = "#OnboardingModal";
var ONBOARDING_TITLE = "#OnboardingTitle";
//Generalized button (so we can have different text)
var ONBOARDING_STEPS = ["#OnboardingPage1", "#OnboardingPage2", "#OnboardingPage3"];
var ONBOARDING_NEXT_BUTTON = "#OnboardingModal .modal-footer a.btn";
var ONBOARDING_TITLES = ["Welcome to Project Awesome :)", 
                         "Creating Visions",
                         "Sharing and Privacy"]
var ONBOARDING_NEXT_TEXT = ["What's that?", "OK, got it.", "That's it. Let's go!"];

var POSTMARKLET = "#postmarklet";

/******************************************************************************
 * Utility functions
 */
function abort() {
  throw new Error("Abort");
}     
      
function AssertException(message) { this.message = message; }
  AssertException.prototype.toString = function () {
  return 'AssertException: ' + this.message;
} 

function assert(exp, message) {
  if (!exp) {
    throw new AssertException(message);
  }
}

/******************************************************************************
 * Utility functions for getting/setting global state
 */

// TODO: BE SAFER EVERYONE FOR IF USER IS LOGGED IN (back end should be OK tho)
function userLoggedIn() {
    return USER.id > 0;
}

/******************************************************************************
 * AJAX functions
 */

function feedbackSaving() {
    if(DEBUG) console.log("Saving");
}
function feedbackSaved() {
    if(DEBUG) console.log("Saved!");
}
function feedbackError() {
    if(DEBUG) {
        alert("Error Saving!");
        console.log("Error!");
    }
}

function doAjax(url, data, successFunc, errorFunc) {
    feedbackSaving();

    $.ajax({
        type: "POST",
        cache: false,
        contentType : "application/json",
        url: url,
        data: data,
        dataType: "json",
        beforeSend: function(jqXHR, settings) {
            if (jqXHR.overrideMimeType) {
                jqXHR.overrideMimeType("application/json");
            }
        },
        success: function(data, textStatus, jqXHR) {
            if (data.result == "success") {
                feedbackSaved();
                successFunc(data, textStatus, jqXHR);
            } else {
                feedbackError();
                console.log("ERROR: " + JSON.stringify(data));
                errorFunc(jqXHR, textStatus, "JSON error");
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            feedbackError();
            errorFunc(jqXHR, textStatus, errorThrown);
        },
        complete: function(jqXHR, textStatus) {},
    });
}


/******************************************************************************
 * Document ready
 */
$(document).ready(function() {
    $.ajaxSetup({ cache: false});

    App.Var.Model = new App.Backbone.Model.Page();
    App.Var.View = new App.Backbone.View.Page({model: App.Var.Model});

    // Do this after we have created Page model and view
    Backbone.history.start({pushState: true});


    //Analytics
    trackUser();
    
    //Click Handlers
    navigationClickHandlers();

    //If Option
    //Display intro
    if(App.Var.Model.option() == App.Const.Options.ONBOARDING)
    {
        //TODO: fix this!
        var onboardingStep = 0;

        //Open Modal
        $(ONBOARDING_MODAL).modal();

        //Wire Next Clicks
        $(ONBOARDING_NEXT_BUTTON).click(function() {

             //Step n
            if(onboardingStep == ONBOARDING_STEPS.length - 1)
                $(OnboardingModal).modal('hide');

            else {
                $(ONBOARDING_STEPS[onboardingStep]).hide();
                $(ONBOARDING_STEPS[onboardingStep+1]).show();
                $(ONBOARDING_TITLE).html(ONBOARDING_TITLES[onboardingStep+1])
                $(ONBOARDING_NEXT_BUTTON).html(ONBOARDING_NEXT_TEXT[onboardingStep+1]);
            }

            onboardingStep++;

        });

        //Cancel postmarklet click
        $(POSTMARKLET).click(function(event) {

            //Don't let it activate the postmarklet on this page
            event.preventDefault();
        })
    }

    /*
     * File upload stuff
     */
    function toggleAddVisionSubmit() {
        var enable = false;
        var fileName = $("#FileUploadInput").val();
        var text = $.trim($("#InputText").val());

        if (fileName != "" && text != "") {
            $("#AddVisionSubmit").removeAttr("disabled");
        } else {
            $("#AddVisionSubmit").attr("disabled", "disabled");
        }
    }

    $("#AddVision").click(function(e) {
        e.preventDefault();
        $("#AddVisionModal").modal();
        $("#FileUploadInput").val("");
        $("#FileUploadInput").removeAttr("disabled");
        $("#FileUploadNoPreview").show();
        $("#FileUploadLoading").hide();
        $("#FileUploadInvalid").hide();
        $("#FileUploadImageContainer").hide();
        $("#InputText").val("");
        $("#AddVisionSubmit").attr("disabled", "disabled");
        if (USER['visionPrivacy'] == false) {
            $("#InputVisionPrivacy").prop("checked", "checked");
        } else {
            $("#InputVisionPrivacy").removeProp("checked");
        }

        //Mixpanel
        mixpanel.track("Add Vision Clicked");
    });
    $("#FileUploadInput").change(function() {
        var fileName = $("#FileUploadInput").val();
        if (fileName != "") {
            // Show user we are processing file
            if (DEBUG) console.log("UPLOAD: " + fileName);

            // Submit!
            $("#FileUploadForm").submit();

            // disable file upload while we are uploading this file
            $("#FileUploadInput").attr("disabled", "disabled");
            $("#FileUploadNoPreview").hide();
            $("#FileUploadLoading").show();
            $("#FileUploadInvalid").hide();
            $("#FileUploadImageContainer").hide();
        }
    });
    $("#FileUploadTarget").load(function() {
        // Re-enable the file upload input
        $("#FileUploadInput").removeAttr("disabled");

        if (DEBUG) console.log("File uploaded!");
        var jsonText = $("#FileUploadTarget").contents().find("body").html();
        var result  = eval('(' + jsonText+ ')');
        if (result && result.result == "success") {
            // Show image uploaded
            if (DEBUG) console.log("url: " + result.url);
            // Append unique string to end of url to smash image caching
            var t  = new Date().getTime();
            var url = $.trim(result.url) + "?" + t.toString();

            $("#FileUploadNoPreview").hide();
            $("#FileUploadNoPreview").hide();
            $("#FileUploadLoading").hide();
            $("#FileUploadImage").attr("src", url);
            $("#FileUploadImageContainer").show();
        } else {
            // Clear the file upload image feedback
            if (DEBUG) console.log("UPLOAD ERROR");
            $("#FileUploadInvalid").show();
            $("#FileUploadNoPreview").hide();
            $("#FileUploadLoading").hide();
            $("#FileUploadImageContainer").hide();
            $("#FileUploadInput").val("");
        }
        toggleAddVisionSubmit();
    });
    $("#InputText").keyup(toggleAddVisionSubmit);
    $("#InputText").bind('paste',toggleAddVisionSubmit);
    $("#InputText").bind('cut',toggleAddVisionSubmit);

    $("#AddVisionSubmit").click(function() {
        var useImage = false;
        if ($("#FileUploadInput").val() != "") {
            useImage = true;
        }

        var text = $.trim($("#InputText").val());
        var isPublic = !($("#InputVisionPrivacy").is(":checked"));

        $("#AddVisionSubmit").attr("disabled", "disabled");

        doAjax("/api/user/" + USER['id'] + "/add_vision",
                JSON.stringify({'useImage' : useImage,
                                'text' : text,
                                'privacy' : isPublic }),
                // success
                function(data, textStatus, jqXHR) {
                    if (DEBUG) console.log("Success: " + JSON.stringify(data));
                    App.Var.Model.addVision(data.newVision);
                    $("#AddVisionModal").modal("hide");

                    //Mixpanel
                    mixpanel.track("Add Vision Success");
                },
                // error
                function(jqXHR, textStatus, errorThrown) {
                    console.log("Error");
                    $("#AddVisionSubmit").removeAttr("disabled");
                }
        );
    });

    $("#VisionDetailsModal").click(function() {
        App.Var.View.hideVisionDetails();
    });
});


function navigationClickHandlers()
{

    setupNavigationBarHandlers();

    $(BUTTON_VIEW_EXAMPLE_VISION_BOARD).click(function(e) {
        e.preventDefault();

        mixpanel.track("View Example Board Clicked");
        App.Var.Router.navigate("/view_board", {trigger: true});
    });

    $("#ReloadHome").live("click", function(e) {
        e.preventDefault();
        App.Var.View.showHome();
    });
    $("#ReloadProfile").live("click", function(e) {
        e.preventDefault();
        App.Var.View.showProfile();
    });

    //From Example Vision 
    /*$(JOIN_SITE_BUTTON).click(function() {
        mixpanel.track("test!");
        $(REGISTER_FORM).first().submit();
    });*/


    //Mixpanel
    //Register (main) Button
    mixpanel.track_links(BUTTON_REGISTER,  "Register Button Clicked");
    mixpanel.track_forms(REGISTER_FORM, "Register (Example Vision Board) Clicked");

}


function setupNavigationBarHandlers()
{
    //Logo
    $(LOGO).click(function(e) {
        
        e.preventDefault();
        
        selectNavItem(NAVIGATION_HOME);

        if (userLoggedIn() && 
            App.Var.Model.pageMode() == App.Const.PageMode.HOME_USER) {
            App.Var.View.showHome();
        } else {
            // Navigate
            App.Var.Router.navigate("/", {trigger: true});
        }
    });


    //Profile
    $(NAVIGATION_PROFILE_LINK).click(function(e) {
        
        e.preventDefault();
        
        //Do this first - speed :)
        selectNavItem(NAVIGATION_PROFILE);

        if (userLoggedIn() && 
            App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.currentUserId() == App.Var.Model.loggedInUserId()) {
            App.Var.View.showProfile();
        } else {
            // Navigate
            App.Var.Router.navigate("/user/" + USER['id'], {trigger: true});
        }
    });

    //Feed
    $(NAVIGATION_FEED_LINK).click(function(e) {
        
        e.preventDefault();
        
        selectNavItem(NAVIGATION_FEED);

        if (App.Var.Model.pageMode() == App.Const.PageMode.FEED) {
            // Refresh content
            App.Var.View.showFeed();
        } else {
            // Navigate
            App.Var.Router.navigate("/recent", {trigger: true});
        }
    });


    function goHome(e) {
        e.preventDefault();
        
        selectNavItem(NAVIGATION_HOME);

        if (userLoggedIn() && 
            App.Var.Model.pageMode() == App.Const.PageMode.HOME_USER) {
            App.Var.View.showHome();
        } else {
            // Navigate
            App.Var.Router.navigate("/", {trigger: true});
        }
    }
    $(NAVIGATION_MAIN_LINK).click(goHome);
    $(NAVIGATION_HOME_LINK).click(goHome);
}

/*
    Highlight Item
*/
function selectNavItem(navItemSelector)
{
    //Clear
    clearNavSelection();

    $(navItemSelector).addClass("active");
}

/*
    Clear Nav Selection

    Visually unselects all of the navigation link (removes the button effect)
    Used to show that a certain page is selected (first removing all of the current selections)
*/
function clearNavSelection()
{
        
    //Elements
    var navigationElements = [NAVIGATION_PROFILE, NAVIGATION_FEED, NAVIGATION_HOME];

    //Remove
    for(var i=0; i<navigationElements.length; i++)
        $(navigationElements[i]).removeClass("active");
}


/*
    Track the user's actions on the site 

    Mixpanel 

    */
function trackUser()
{   
    //Make sure the user is logged in!
    if(!userLoggedIn()) return;

    //Properties
    var userId = USER['id'];
    var email = USER['email'];
    var firstName = USER['firstName'];
    var lastName = USER['lastName'];
    var fullName = firstName + " " + lastName;
    
    //Associate with email
    mixpanel.identify(email);

    //Add additional info
    mixpanel.register_once({
        'User Id': userId,
        'Email': email,
        'First Name': firstName,
        'Last Name': lastName
    });


    //For People
    mixpanel.people.set({
    '$email': email,
    'User Id': userId,
    '$first_name': firstName,
    '$last_name': lastName,
    '$name': fullName
    //'$created': new Date(),
    });
}

/* $eof */
