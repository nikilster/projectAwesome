/******************************************************************************
* DOM Element Constants
*******************************************************************************/


// ------ Logo ------
var LOGO = "#Logo";

// ------ Navigation li's ------
var NAVIGATION_PROFILE = "#NavigationProfile";
var NAVIGATION_FEED = "#NavigationFeed";
var NAVIGATION_MAIN = "#NavigationMain";
var NAVIGATION_HOME = "#NavigationHome";

// ------ Navigation Links ------
var NAVIGATION_PROFILE_LINK = NAVIGATION_PROFILE + " a";
var NAVIGATION_FEED_LINK = NAVIGATION_FEED + " a";
var NAVIGATION_MAIN_LINK = NAVIGATION_MAIN + " a";
var NAVIGATION_HOME_LINK = NAVIGATION_HOME + " a";


// ------ Container Divs ------

var CONTENT_DIV = "#Content";  //Main container for the visions
var EXAMPLE_VISION_BOARD_DIV = "#ExampleVisionBoard";
var VISION_INFORMATION_DIV = "#VisionInformation";

var VISION_DETAILS_MODAL = "#VisionDetailsModal";

var USER_INFORMATION = "#UserInformation";
//Explanation
var EXPLANATION_DIV = "#Explanation";
var EXPLANATION_PADDING = "#ExplanationPadding";

var HOME_PAGE_NAV = "#HomePageNav";
var HOME_PAGE_PADDING = "#HomePagePadding";

var USER_LIST_MODAL = "#UserListModal";

//Instructions
var NUM_VISION_REQUIRED_FOR_USER = 3;
var INSTRUCTIONS_DIV = "#Instructions";
var INSTRUCTIONS_TAGLINE = "#Instructions .Tagline";
var INSTRUCTIONS_PADDING = "#InstructionsPadding";
var INSTRUCTIONS_ZERO_VISIONS_SELECTED = "#SelectedZero";
var INSTRUCTIONS_ONE_VISION_SELECTED = "#SelectedOne";
var INSTRUCTIONS_TWO_VISIONS_SELECTED = "#SelectedTwo";
var INSTRUCTIONS_THREE_VISIONS_SELECTED = "#SelectedThree";
var BUTTON_VIEW_EXAMPLE_VISION_BOARD = "#ViewExampleVisionBoardButton";

//Register Button on index page
var BUTTON_REGISTER = "#RegularRegisterButton";

var REGISTER_FORM = "#RegisterForm";
var USER_SELECTED_VISIONS_INPUT = "#UserSelectedVisions";
var EXAMPLE_VISION_BOARD_INSTRUCTIONS = "#ExampleVisionBoardInstructions";

//Register button on example vision board page (register now)
var JOIN_SITE_BUTTON = "#JoinSite"; //Triggers form


App.Backbone.View.Page = Backbone.View.extend({
    
    //Added by Nikil
    //1-18-2013 For Onboarding
    /*
        Fix!

    events: function() {

        //So we can use the ONBOARDING constant :)
        // --> Vision.js
        var _events = {};
        _events["click " + ONBOARDING_NEXT_BUTTON] = "masonryReload";

        return _events;

    },
    */
    initialize: function() {
        _.bindAll(this, "masonryReload",
                        // Vision details modal
                        "showVisionDetails",
                        "hideVisionDetails",
                        "hideVisionDetailsModal",

                        "repostVision",
                        "ajaxRepostVisionSuccess",
                        "ajaxRepostVisionError",

                        //"addVisionComment",
                        //"ajaxAddVisionCommentSuccess",
                        //"ajaxAddVisionCommentError",
                        // Changing page mode and rendering rest of page
                        "changePageMode",
                        "showInfoBar",
                        "hideInfoBar",
                        "showHomePageNav",
                        "hideHomePageNav",
                        // For onboarding
                        "showAddItemButton",
                        "hideAddItemButton",
                        "changeInSelectedVisions",
                        "selectedVisionsSortStart",
                        "selectedVisionsSortChange",
                        "selectedVisionsSortStop",
                        "renderExampleVisionBoard",
                        "renderSelectedVision",
                        // Feed
                        "showFeed",
                        "renderFeed",
                        "renderFeedError",
                        "renderActivity",
                        "hideFeed",
                        // Show main page
                        "showHome",
                        "renderHome",
                        "renderHomeError",
                        // Rendering Main vision list
                        "renderVisionList",
                        "renderVision",
                        "sortStart",
                        "sortChange",
                        "sortStop",
                        "ajaxSortSuccess",
                        "ajaxSortError",
                        // Show user profile
                        "showProfile",
                        "renderProfile",
                        "renderProfileError",
                        "showUserInformation",
                        "hideUserInformation",
                        // Show vision page
                        "showVisionPage",
                        "showVisionPageSuccess",
                        "showVisionPageError",
                        // User List modal
                        "showUserList",
                        "ajaxUserListSuccess",
                        "ajaxUserListError",
                        "hideUserList",
                        // Show likes
                        "showVisionLikes",
                        "showVisionCommentLikes"

                        //Onboarding modal
                        //"onboardingNext"
                        );

        this.model.bind("change:pageMode", this.changePageMode, this);
        this.model.otherVisions().bind("reset", this.renderVisionList, this);
        this.model.visionList().bind("add",
                                     this.renderVisionList,
                                     this);
        this.model.visionList().bind("remove",
                                     this.renderVisionList,
                                     this);
        this.model.visionList().bind("reset",
                                     this.renderVisionList,
                                     this);
        this.model.selectedVisions().bind("add",
                                          this.changeInSelectedVisions,
                                          this);
        this.model.selectedVisions().bind("remove",
                                          this.changeInSelectedVisions,
                                          this);
        this.model.bind("change:user", this.showUserInformation, this);
        // initialize a few variables
        this.selectedVisionMoveIndex = -1;
        this.srcIndex = -1;
        this.visionDetails = null;

        this.onboardingStep = 0;
    },

    repostVision: function(visionModel) {
        assert(visionModel != null, "Vision model to repost is null");
        if (visionModel != null) {
            if (DEBUG) console.log("REPOST: " + visionModel.visionId());
            doAjax("/api/user/" + USER['id'] + "/repost_vision",
                   JSON.stringify({
                                    'visionId' : visionModel.visionId(),
                                  }),
                   this.ajaxRepostVisionSuccess,
                   this.ajaxRepostVisionError
            );
        }
    },
    ajaxRepostVisionSuccess: function(data, textStatus, jqXHR) {
        this.model.repostVisionDone(data.repostParentId, data.newVision);
    },
    ajaxRepostVisionError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    // Needed by Vision view
    onNewComment: function() {
        this.masonryReload();
    },
    onVisionResize: function() {
        this.masonryReload();
    },

    showVisionDetails: function(visionModel) {
        assert(null != this.model.currentVision(), "Invalid current vision");

        // Note: jQuery text() method escapes html brackets and stuff
        var modal = $(VISION_DETAILS_MODAL).first();

        this.visionDetails = new App.Backbone.View.VisionDetails(
                                         {model: this.model.currentVision()});
        modal.empty().append(this.visionDetails.el);
        $("body").addClass("NoScroll");
        modal.fadeIn("slow");
    },
    hideVisionDetails: function() {
        this.hideVisionDetailsModal();
        window.history.back();
    },
    hideVisionDetailsModal: function() {
        if ($(VISION_DETAILS_MODAL).css("display") != "none") {
            var modal = $(VISION_DETAILS_MODAL).first().fadeOut("fast");
            $("body").removeClass("NoScroll");
        }
        $(VISION_INFORMATION_DIV).hide();
    },

    /*
     * Changing page mode triggered by set of this.model.pageMode
     */
    changePageMode: function() {
        if (DEBUG) console.log("CHANGE MODE: " + this.model.pageMode());

        var pageMode = this.model.pageMode();

        if (pageMode == App.Const.PageMode.HOME_GUEST) {
            this.hideHomePageNav();
            this.showInfoBar(true);
            this.hideAddItemButton();
            this.showHome();
        } else if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            this.hideHomePageNav();
            this.showInfoBar(false);
            this.showExampleVisionBoard();
        } else if (pageMode == App.Const.PageMode.HOME_USER) {
            this.hideInfoBar();
            this.hideAddItemButton();
            this.showHome();
            this.showHomePageNav();
            selectNavItem(NAVIGATION_HOME);

        } else if (pageMode == App.Const.PageMode.FEED) {
            this.hideInfoBar();
            this.hideAddItemButton();
            this.showHomePageNav();
            this.showFeed();
            selectNavItem(NAVIGATION_FEED);

        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            this.hideHomePageNav();
            if (userLoggedIn()) {
                this.hideInfoBar();
                this.showAddItemButton();
            } else {
                this.showInfoBar(true);
                this.hideAddItemButton();
            }
            this.showProfile();            
        } else if (pageMode == App.Const.PageMode.VISION_DETAILS) {
            this.hideHomePageNav();
            assert(null != this.model.currentVision(),
                   "Invalid current vision");
            this.showVisionDetails();
        } else if (pageMode == App.Const.PageMode.VISION_PAGE) {
            this.hideHomePageNav();
            this.showVisionPage();
        } else {
            assert(false, "Invalid page mode in changePageMode");
        }
    },

    /*
     * Render vision list: triggered by set of this.model.visionList
     */
    renderVisionList: function() {
        
        //if(DEBUG) console.log("rendering vision list");

        var masonryContainer = $(CONTENT_DIV).first();
        masonryContainer.empty();

        this.children = []
        this.model.activeVisionList().each(this.renderVision);
        masonryContainer.append(this.children);

        // TODO: Don't need to reload once we know heights of images
        masonryContainer.masonry({
            itemSelector: VISION_CLASS_SELECTOR,
            isFitWidth: true,
        }).imagesLoaded(function() {
            $(CONTENT_DIV).masonry('reload');
        });
        if (App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.currentUserId() == USER.id) {
            masonryContainer.sortable({
                items: VISION_CLASS_SELECTOR,
                handle: ".Move",
                distance: 12,
                helper: "clone",
                forcePlaceholderSize: true,
                placeholder: "Vision VisionPlaceholder",
                tolerance: 'pointer',
                start: this.sortStart,
                change: this.sortChange,
                stop: this.sortStop,
            });
        }
    },
    renderVision: function(vision, index) {
        var vision = new App.Backbone.View.Vision({ model: vision,
                                                    parentView: this });
        this.children.push(vision.el);
    },
    sortStart: function(event, ui) {
        ui.item.removeClass(VISION_CLASS);
        this.masonryReload();

        this.srcIndex = ui.item.index();
    },
    sortStop: function(event, ui) {
        ui.item.addClass(VISION_CLASS);
        this.masonryReload();
        this.destIndex = ui.item.index();
        if (this.destIndex != this.srcIndex && this.srcIndex >= 0) {
            var visionId = this.model.visionList().at(this.srcIndex).visionId();
            doAjax("/api/user/" + USER['id'] + "/move_vision",
                   JSON.stringify({'visionId' : visionId,
                                   'srcIndex' : this.srcIndex,
                                   'destIndex' : this.destIndex}),
                   this.ajaxSortSuccess,
                   this.ajaxSortError
            );
        }
    },
    sortChange: function(event, ui) {
        this.masonryReload();
    },
    ajaxSortSuccess: function(data, textStatus, jqXHR) {
        this.model.moveVision(this.srcIndex, this.destIndex);
    },
    ajaxSortError: function(jqXHR, textStatus, errorThrown) {
        this.renderVisionList();
    },
    masonryReload: function() {
        $(CONTENT_DIV).masonry('reload');
    },

    /*
     * Render test vision board
     */
    renderExampleVisionBoard: function() {
        
        //Get Element
        var exampleVisionBoard = $(EXAMPLE_VISION_BOARD_DIV).first();

        //Clear
        exampleVisionBoard.empty();
        
        //Load Visions
        this.testVisions = []
        this.model.selectedVisions().each(this.renderSelectedVision);

        //Add To Container
        exampleVisionBoard.append(this.testVisions);

        // TODO: Don't need to reload once we know heights of images
        exampleVisionBoard.masonry({
            itemSelector: VISION_CLASS_SELECTOR,
            isFitWidth: true,
        }).imagesLoaded(function() {
            $(EXAMPLE_VISION_BOARD_DIV).masonry('reload');
        });
        exampleVisionBoard.sortable({
            items: VISION_CLASS_SELECTOR,
            distance: 12,
            helper: "clone",
            forcePlaceholderSize: true,
            placeholder: "Vision VisionPlaceholder",
            tolerance: 'pointer',
            start: this.selectedVisionsSortStart,
            change: this.selectedVisionsSortChange,
            stop: this.selectedVisionsSortStop,
        });
    },
    renderSelectedVision: function(vision, index) {
        // Shouldn't need a parent view
        var vision = new App.Backbone.View.Vision({ model: vision,
                                                    parentView: null });
        this.testVisions.push(vision.el);
    },
    selectedVisionsSortStart: function(event, ui) {
        ui.item.removeClass(VISION_CLASS);
        ui.item.parent().masonry('reload');

        this.selectedVisionMoveIndex = ui.item.index();
    },
    selectedVisionsSortStop: function(event, ui) {
        ui.item.addClass(VISION_CLASS);
        ui.item.parent().masonry('reload');
        var destIndex = ui.item.index();
        if (destIndex != this.selectedVisionMoveIndex &&
            this.selectedVisionMoveIndex >= 0) {
            this.model.moveSelectedVision(this.selectedVisionMoveIndex,
                                          destIndex);
        }
    },
    selectedVisionsSortChange: function(event, ui) {
        ui.item.parent().masonry('reload');
    },

    /*
     * Show/hide Add Item button
     */
    showAddItemButton: function() { $("#AddItemButton").show(); },
    hideAddItemButton: function() { $("#AddItemButton").hide(); },

    /*
     * Show/hide information bar
     *
     * Input for now: true = info, false = test vision
     * *** TODO: make this better ***
     */
    showInfoBar: function(onboarding) {
        if (onboarding) {
            $(EXAMPLE_VISION_BOARD_INSTRUCTIONS).hide();
            $(EXPLANATION_DIV).show();
            //$(EXPLANATION_PADDING).show();
            $(INSTRUCTIONS_DIV).show();
            $(INSTRUCTIONS_PADDING).show();
        } else {
            $(EXPLANATION_DIV).hide();
            $(EXPLANATION_PADDING).hide();
            $(INSTRUCTIONS_DIV).hide();
            $(EXAMPLE_VISION_BOARD_INSTRUCTIONS).show();
            $(INSTRUCTIONS_PADDING).show();
        }
    },
    hideInfoBar: function() {
        $(EXPLANATION_DIV).hide();
        $(EXPLANATION_PADDING).hide();
        $(INSTRUCTIONS_PADDING).hide();
        $(INSTRUCTIONS_DIV).hide();
    },

    showHomePageNav: function() {
        //$(HOME_PAGE_NAV).show();
        //$(HOME_PAGE_PADDING).show();
    },
    hideHomePageNav: function() {
        //$(HOME_PAGE_NAV).hide();
        //$(HOME_PAGE_PADDING).hide();
    },

    changeInSelectedVisions: function() {

        //Number of visions selected
        var length = this.model.numSelectedVisions();

        //Get the corrrect spans
        var instructions = [$(INSTRUCTIONS_ZERO_VISIONS_SELECTED), 
                            $(INSTRUCTIONS_ONE_VISION_SELECTED),
                            $(INSTRUCTIONS_TWO_VISIONS_SELECTED),
                            $(INSTRUCTIONS_THREE_VISIONS_SELECTED)];

        //User has selected somewhere from 0 to NUM_VISION_REQUIRED_FOR_USER Selected
        if (length >=0 && length < NUM_VISION_REQUIRED_FOR_USER) {
            this.hideAllExcept(instructions,length);

            //Make sure tagline is shown if they remove visions
            $(INSTRUCTIONS_TAGLINE).show();

            //Show Register
            $(BUTTON_VIEW_EXAMPLE_VISION_BOARD).hide();
            $(BUTTON_REGISTER).show();
        }

        //User has selected more
        else if(length >= NUM_VISION_REQUIRED_FOR_USER) {
            this.hideAllExcept(instructions, NUM_VISION_REQUIRED_FOR_USER);
            
            //Hide the tagline to focus on "go to board"
            $(INSTRUCTIONS_TAGLINE).hide();

            //Show View Example Board
            $(BUTTON_REGISTER).hide();
            $(BUTTON_VIEW_EXAMPLE_VISION_BOARD).show();
        }

        //Should never have < 0 visions selected!
        else {
            console.log("ERROR - should not have negative count visions!");
        }

        // Update hidden field in registration
        var visionIds = [];
        for (var i = 0 ; i < length ; i++) {
            visionIds.push(this.model.selectedVisions().at(i).visionId());
        }
        $(USER_SELECTED_VISIONS_INPUT).first().attr("value", JSON.stringify(visionIds));
        //if (DEBUG) console.log("VISION LIST: " + JSON.stringify(visionIds));

        // If we are in test vision mode, we need to re-render vision
        if (App.Var.Model.pageMode() == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            this.renderExampleVisionBoard();
        }
    },

    /*
        Hide all of the elements in the array, except for the one at index i
    */
    hideAllExcept: function(elements, indexToShow) {
        for(var i=0; i<elements.length; i++) {
            if(i == indexToShow) {
                elements[i].fadeIn("fast");//(CSS_ClASS_HIDDEN);
            } else {
                elements[i].hide();//addClass(CSS_ClASS_HIDDEN);
            }
        }
    },
    /*
     * Render home page
     */
    showFeed: function() {
        this.hideUserInformation();
        this.hideVisionDetailsModal();

        // Stops re-render when coming back from vision details
        if (this.model.cameFromVisionDetails()) {
            this.model.clearLastPageMode();
            return;
        }

        $(EXAMPLE_VISION_BOARD_DIV).empty().hide();
        $(CONTENT_DIV).empty().masonry().hide();
        $("#Feed").show();

        var ajaxUrl = "/api/get_feed";
        $.ajax({
            type: "GET",
            cache: false,
            contentType : "application/json",
            url: ajaxUrl,
            beforeSend: function(jqXHR, settings) {
                if (jqXHR.overrideMimeType) {
                    jqXHR.overrideMimeType("application/json");
                }
            },
            complete: function(jqXHR, textStatus) {},
            error: function(jqXHR, textStatus, errorThrown) {
                App.Var.View.renderFeedError();
            },
            success: function(data, textStatus, jqXHR) {
                App.Var.JSON = data;
                App.Var.View.renderFeed();
            }
        });
        
    },
    hideFeed: function() {
        $("#Feed").hide();
        $("#FeedContent").empty();
    },
    renderFeed: function() {

        this.model.setActivities(App.Var.JSON.activities);
        this.children = [];
        this.model.activities().each(this.renderActivity);
        $("#FeedContent").empty().show().append(this.children);
    },
    renderFeedError: function() {
    },
    renderActivity: function(activity, index) {
        var view = new App.Backbone.View.Activity({model: activity});
        this.children.push(view.el);
    },
    /*
     * Render home page
     */
    showHome: function() {
        this.hideFeed();
        this.hideVisionDetailsModal();

        // Stops re-render when coming back from vision details
        if (this.model.cameFromVisionDetails()) {
            this.model.clearLastPageMode();
            return;
        }

        this.hideUserInformation();
        $(EXAMPLE_VISION_BOARD_DIV).empty().hide();
        
        this.displayHomeVisions();
    },

    displayHomeVisions: function() {
        $(CONTENT_DIV).empty().masonry().show();

        var ajaxUrl = "/api/get_main_page_visions";

        $.ajax({
            type: "GET",
            cache: false,
            contentType : "application/json",
            url: ajaxUrl,
            beforeSend: function(jqXHR, settings) {
                if (jqXHR.overrideMimeType) {
                    jqXHR.overrideMimeType("application/json");
                }
            },
            complete: function(jqXHR, textStatus) {},
            error: function(jqXHR, textStatus, errorThrown) {
                App.Var.View.renderHomeError();
            },
            success: function(data, textStatus, jqXHR) {
                App.Var.JSON = data;
                App.Var.View.renderHome();
            }
        });
    },
    renderHome: function() {
        if (DEBUG) console.log("Render Home");
        if (this.model.visionList().isEmpty()) {
            // TODO: be smarter about when to load and set visionList later
            //       do this first so rendering of other visions has proper
            //       vision list to process
            this.model.setVisionList(App.Var.JSON.visionList);
        }
        this.model.setOtherVisions(App.Var.JSON.otherVisions);
    },
    renderHomeError: function() {
        var masonryContainer = $(CONTENT_DIV).first();
        masonryContainer.empty().masonry();
    },

    /*
     * Show test vision
     */
    showExampleVisionBoard: function() {
        $(CONTENT_DIV).hide();
        $(EXAMPLE_VISION_BOARD_DIV).empty().show();
        this.renderExampleVisionBoard();
    },

    /*
     * Render user profile page
     */
    showProfile: function() {
        this.hideFeed();
        this.hideVisionDetailsModal();

        // Stops re-render when coming back from vision details
        if (this.model.cameFromVisionDetails()) {
            this.model.clearLastPageMode();
            return;
        }

        //If this is the user's page:
        //Track "vision board view"!
        if(App.Var.Model.loggedInUserId() === App.Var.Model.currentUserId()) {
            
            //Increment view vision board count
            mixpanel.people.increment('Vision Board Views');

            selectNavItem(NAVIGATION_PROFILE);
        }
        else
            //No Selection
            clearNavSelection();

        $(EXAMPLE_VISION_BOARD_DIV).empty().hide();
        $(CONTENT_DIV).empty().masonry().show();

        var ajaxUrl = "/api/user/" + App.Var.Model.currentUserId() + "/visions";

        $.ajax({
            type: "GET",
            cache: false,
            contentType : "application/json",
            url: ajaxUrl,
            beforeSend: function(jqXHR, settings) {
                if (jqXHR.overrideMimeType) {
                    jqXHR.overrideMimeType("application/json");
                }
            },
            complete: function(jqXHR, textStatus) {},
            error: function(jqXHR, textStatus, errorThrown) {
                if(DEBUG) console.log("error getting profile info");
                App.Var.View.renderProfileError();
            },
            success: function(data, textStatus, jqXHR) {
                if(DEBUG) console.log("Successfully got Profile!");
                App.Var.JSON = data;
                App.Var.View.renderProfile();
            }
        });
    },
    renderProfile: function() {
        if (DEBUG) console.log("Rendering Profile");

        this.model.setVisionList(App.Var.JSON.visionList);
        if (App.Var.Model.currentUserId() != USER.id) {
            this.model.setOtherVisions(App.Var.JSON.otherVisions);
        }
        this.model.setUser(App.Var.JSON.user);
    },
    renderProfileError: function() {
        var masonryContainer = $(CONTENT_DIV).first();
        masonryContainer.empty().masonry();
    },
    showUserInformation: function() {
        if (DEBUG) console.log("SET USER INFO");

        this.userInformation = new App.Backbone.View.UserInformation(
                                                 {model: this.model.user()});
        $(USER_INFORMATION).empty().append(this.userInformation.el).show();
    },
    hideUserInformation: function() {
        $(USER_INFORMATION).hide();
    },

    /*
     * Render vision page (when we go directly to a vision)
     */
    showVisionPage: function() {
        this.hideInfoBar();
        this.hideVisionDetailsModal();
        $(EXAMPLE_VISION_BOARD_DIV).empty().hide();
        $(CONTENT_DIV).empty().masonry().hide();
        $(VISION_INFORMATION_DIV).show();

        var ajaxUrl = "/api/vision/" + currentVisionId;

        $.ajax({
            type: "GET",
            cache: false,
            contentType : "application/json",
            url: ajaxUrl,
            beforeSend: function(jqXHR, settings) {
                if (jqXHR.overrideMimeType) {
                    jqXHR.overrideMimeType("application/json");
                }
            },
            complete: function(jqXHR, textStatus) {},
            error: function(jqXHR, textStatus, errorThrown) {
                if(DEBUG) console.log("error getting vision info");
                App.Var.View.showVisionPageError();
            },
            success: function(data, textStatus, jqXHR) {
                if(DEBUG) console.log("Successfully got vision!");
                App.Var.JSON = data;
                App.Var.View.showVisionPageSuccess();
            }
        });
    },
    showVisionPageSuccess: function() {
        var vision = new App.Backbone.Model.Vision(App.Var.JSON.vision);
        this.model.setCurrentVision(vision);
        this.currentVision = new App.Backbone.View.VisionDetails(
                                         {model: this.model.currentVision()});
        $(VISION_INFORMATION_DIV).empty().append(this.currentVision.el);
    },
    showVisionPageError: function() {
    },
    showUserList: function(listType, id) {
        // Set variables to pass to AJAX success function
        this.userListType = listType;
        this.userListId = id;

        // Now do the proper AJAX request
        if (listType == App.Const.UserList.FOLLOWS) {
            console.log("List follows: user" + id);
            doAjax("/api/user/" + id + "/follows",
                   JSON.stringify({
                                    'userId' : id,
                                  }),
                   this.ajaxUserListSuccess,
                   this.ajaxUserListError
            );
        } else if (listType == App.Const.UserList.FOLLOWERS) {
            console.log("List followers: user" + id);
            doAjax("/api/user/" + id + "/followers",
                   JSON.stringify({
                                    'userId' : id,
                                  }),
                   this.ajaxUserListSuccess,
                   this.ajaxUserListError
            );
        } else if (listType == App.Const.UserList.VISION_LIKES) {
            console.log("List vision likers: vision" + id);
            doAjax("/api/vision/" + id + "/likes",
                   JSON.stringify({
                                    'visionId' : id,
                                  }),
                   this.ajaxUserListSuccess,
                   this.ajaxUserListError
            );
        } else if (listType == App.Const.UserList.VISION_COMMENT_LIKES) {
            console.log("List vision comment likers: comment" + id);
            doAjax("/api/vision_comment/" + id + "/likes",
                   JSON.stringify({
                                    'visionCommentId' : id,
                                  }),
                   this.ajaxUserListSuccess,
                   this.ajaxUserListError
            );
        }
    },
    ajaxUserListSuccess: function(data, textStatus, jqXHR) {
        console.log("DATA: " + JSON.stringify(data));
        var listName = "";
        if (this.userListType == App.Const.UserList.FOLLOWS) {
            listName = "Follows";
        } else if (this.userListType == App.Const.UserList.FOLLOWERS) {
            listName = "Followers";
        } else if (this.userListType == App.Const.UserList.VISION_LIKES) {
            listName = "Vision Likes";
        } else if (this.userListType == App.Const.UserList.VISION_COMMENT_LIKES) {
            listName = "Comment Likes";
        }
        if (listName != "") {
            var users = new App.Backbone.Model.UserList(data.users);
            var view = new App.Backbone.View.UserList({
                                                    collection: users,
                                                    listName: listName });
            $("#UserListModal").empty().append(view.el).modal();
        }
    },
    ajaxUserListError: function(jqXHR, textStatus, errorThrown) {
    },
    hideUserList: function() {
        $("#UserListModal").empty().modal("hide");
    },

    showVisionLikes: function(visionId) {
        if (userLoggedIn()) {
            console.log("SHOW VISION LIKES: " + visionId);
            this.showUserList(App.Const.UserList.VISION_LIKES, visionId);
        }
    },
    showVisionCommentLikes: function(visionCommentId) {
        if (userLoggedIn()) {
            console.log("SHOW VISION COMMENT LIKES: " + visionCommentId);
            this.showUserList(App.Const.UserList.VISION_COMMENT_LIKES,
                              visionCommentId);
        }
    },

    /*
    onboardingNext: function() {

        console.log("next clicked!");

        //Step n
        if(this.onboardingStep == ONBOARDING_STEPS.length - 1)
            $(OnboardingModal).modal('hide');

        else {
            $(ONBOARDING_STEPS[this.onboardingStep]).hide();
            $(ONBOARDING[this.onboardingStep+1]).show();
        }

        this.onboardingStep++;
        
    }
    */
});

