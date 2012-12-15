/******************************************************************************
 * home.js
 *
 * Implements JS for main vision board view
 ******************************************************************************/

/*
    Debug
*/
var DEBUG = true;

/******************************************************************************
* DOM Element Constants
*******************************************************************************/
var CONTENT_DIV = "#Content";  //Main container for the visions
var EXAMPLE_VISION_BOARD_DIV = "#ExampleVisionBoard";

var VISION_CLASS = "Vision";
var VISION_CLASS_SELECTOR = "." + VISION_CLASS;
var CURSOR_CLASS_MOVE = "MoveCursor";
var VISION_SELECTED_CLASS = "VisionSelected";

var VISION_COMMENT_CONTAINER = ".VisionCommentContainer";

var VISION_DETAILS_MODAL = "#VisionDetailsModal";
var VISION_DETAILS_COMMENTS_CONTAINER = "#VisionDetailsCommentsContainer";
var VISION_DETAILS_ADD_COMMENT = "#VisionDetailsAddComment";
var VISION_DETAILS_NAME = "#VisionDetailsName";
var VISION_DETAILS_PICTURE = "#VisionDetailsPicture";
var VISION_DETAILS_TEXT_CONTAINER = "#VisionDetailsTextContainer";
var VISION_DETAILS_EDIT_TEXT = "#VisionDetailsEditText";
var VISION_DETAILS_EDIT_FORM = "#VisionDetailsEditForm";
var VISION_DETAILS_TEXT = "#VisionDetailsText";
var VISION_DETAILS_ADD_COMMENT_PICTURE = "#VisionDetailsAddCommentPicture";
var VISION_DETAILS_ADD_COMMENT_CONTAINER = "#VisionDetailsAddCommentContainer";
var VISION_DETAILS_MODAL_BOX = "#VisionDetailsModalBox";
var VISION_DETAILS_CLOSE = "#VisionDetailsClose";
var VISION_DELETE_BUTTON = "#VisionDeleteButton";

//Instructions
var NUM_VISION_REQUIRED_FOR_USER = 3;
var INSTRUCTIONS_DIV = "#Instructions";
var INSTRUCTIONS_PADDING = "#InstructionsPadding";
//Sync # w/ Spans -> 
var INSTRUCTIONS_ZERO_VISIONS_SELECTED = "#SelectedZero";
var INSTRUCTIONS_ONE_VISION_SELECTED = "#SelectedOne";
var INSTRUCTIONS_TWO_VISIONS_SELECTED = "#SelectedTwo";
var INSTRUCTIONS_THREE_VISIONS_SELECTED = "#SelectedThree";
var VIEW_EXAMPLE_VISION_BOARD_BUTTON = "#ViewExampleVisionBoardButton";
var REGISTER_FORM = "#RegisterForm";
var USER_SELECTED_VISIONS_INPUT = "#UserSelectedVisions";
var EXAMPLE_VISION_BOARD_INSTRUCTIONS = "#ExampleVisionBoardInstructions";
var JOIN_SITE_BUTTON = "#JoinSite"; //Triggers form

//Overlay Buttons
var ANIMATION_TIME = 150;
var ADD_NOT_LOGGED_IN_VISION_SELECTOR = ".AddVisionNotAuthenticated";
var ADD_EXISTING_VISION_SELECTOR = ".AlreadyHaveVision";
var REMOVE_NOT_LOGGED_IN_VISION_SELECTOR = ".RemoveVisionNotAuthenticated";
var REPOST_BUTTON = ".Repost";
var MOVE_ICON = ".Move";

//Utility
var CSS_CLASS_HIDDEN = "CSS_CLASS_HIDDEN";

// Constants
var MAX_USER_DESCRIPTION_LENGTH = 200;

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
    
    /*    
    $("#UserFeedbackSaved").hide();
    $("#UserFeedbackError").hide();
    $("#UserFeedbackSaving").show();
    */
}
function feedbackSaved() {
    
    if(DEBUG) console.log("Saved!");
    /*
    $("#UserFeedbackError").hide();
    $("#UserFeedbackSaving").hide();
    $("#UserFeedbackSaved").stop(true,true).show().fadeOut(5000);
    */
}
function feedbackError() {
    
    if(DEBUG) {
        alert("Error Saving!");
        console.log("Error!");
    }
    /*
    $("#UserFeedbackSaving").hide();
    $("#UserFeedbackSaved").hide();
    $("#UserFeedbackError").show();
    */
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
 * Namespace
 */
var App = {
    // Namespace for Backbone data structures
    Backbone: {
        Model: {},
        View: {},
        Router: null,
    },
    Const: {
        PageMode: {
            EMPTY: 0,
            //Main Page (not logged in)
            HOME_GUEST: 1, 
            //Main Page (logged in)
            HOME_USER: 2,
            //Example vision board (not logged in)
            EXAMPLE_VISION_BOARD: 3,
            //User Page (logged in)
            USER_PROFILE: 4,

            GUEST_PROFILE: 5,
            INVALID: 6, // Keep at end: we use to check validity of pageMode
        },
        VisionPrivacy: {
            PRIVATE: 1,
            PUBLIC: 2,
        },
        MAX_SELECTED_VISIONS: 10,
    },
    // Variables in app
    Var: {
        JSON: null,
        Model: null,
        View: null,
        Router: null,
    },
}

/******************************************************************************
 * Backbone models
 */

App.Backbone.Model.User = Backbone.Model.extend({
    defaults: {
        id: -1,
        firstName: "",
        lastName: "",
        picture: "",
        description: "",
        visionPrivacy: -1,
    },
    initialize: function() {
    },
    userId: function() { return this.get("id"); },
    firstName: function() { return this.get("firstName"); },
    lastName: function() { return this.get("lastName"); },
    fullName: function() { return this.firstName() + " " + this.lastName(); },
    picture: function() { return this.get("picture"); },
    description: function() { return this.get("description"); },
    visionPrivacy: function() { return this.get("visionPrivacy"); },
});

App.Backbone.Model.Picture = Backbone.Model.extend({
    defaults: {
        id: -1,
        filename: "",
        largeUrl: "",
        mediumUrl: "",
        smallUrl: "",
    },
    initialize: function() {
    },
    pictureId: function() { return this.get("id"); },
    largeUrl: function() { return this.get("largeUrl"); },
    mediumUrl: function() { return this.get("mediumUrl"); },
    smallUrl: function() { return this.get("smallUrl"); },
});

App.Backbone.Model.VisionComment = Backbone.Model.extend({
    defaults: {
        id: -1,
        authorId: -1,
        text: "",
        name: "",
        picture: "",
    },
    initialize: function() {
    },
    visionCommentId: function() { return this.get("id"); },
    authorId: function() { return this.get("authorId"); },
    text: function() { return this.get("text"); },
    name: function() { return this.get("name"); },
    picture: function() { return this.get("picture"); },
});
App.Backbone.Model.VisionCommentList = Backbone.Collection.extend({
    model: App.Backbone.Model.VisionComment
});

App.Backbone.Model.Vision = Backbone.Model.extend({
    defaults: {
        id: -1,
        parentId: -1,
        rootId: -1,
        userId: -1,
        text: "",
        name: "",
        privacy: -1,
        picture: null,
        comments: null,
        isSelected: false,
    },
    initialize: function() {
        this.set({
            picture: new App.Backbone.Model.Picture(this.get("picture")),
            comments: new App.Backbone.Model.VisionCommentList(this.get("comments")),
        });

        if (null != App.Var.Model &&
            null != App.Var.Model.getSelectedVision(this.visionId())) {
            this.set({isSelected: true});
        }
    },
    // Getters
    visionId: function() { return this.get("id"); },
    parentId: function() { return this.get("parentId"); },
    rootId: function() { return this.get("rootId"); },
    userId: function() { return this.get("userId"); },
    picture: function() { return this.get("picture"); },
    text: function() { return this.get("text"); },
    name: function() { return this.get("name"); },
    isSelected: function() { return this.get("isSelected"); },
    comments: function() { return this.get("comments"); },

    isPublic: function() {
        var privacy = this.get("privacy");
        assert(privacy == App.Const.VisionPrivacy.PRIVATE ||
               privacy == App.Const.VisionPrivacy.PUBLIC, "Invalid privacy");
        return privacy == App.Const.VisionPrivacy.PUBLIC;
    },

    // Setters
    toggleSelected: function() {
        if (!this.isSelected()) {
            if (App.Var.Model.numSelectedVisions() <
                App.Const.MAX_SELECTED_VISIONS) {
                App.Var.Model.addToSelectedVisions(this);
            } else {
                return;
            }
        } else {
            App.Var.Model.removeFromSelectedVisions(this);
        }
        this.set({isSelected: !this.get("isSelected")});
    },
    addComment: function(comment) {
        this.comments().push(new App.Backbone.Model.VisionComment(comment));
    },
    setComments: function(comments) {
        this.comments().reset(comments);
    },
    edit: function(text, isPublic) {
        var privacy = App.Const.VisionPrivacy.PRIVATE;
        if (isPublic) {
            privacy = App.Const.VisionPrivacy.PUBLIC;
        }
        this.set({ 'text' : text,
                   'privacy' : privacy,
                 });
    },
    deepClone: function() {
        var cloneModel = this.clone();
        cloneModel.set({ picture: this.picture().clone() });
        return cloneModel;
    },
});

App.Backbone.Model.VisionList = Backbone.Collection.extend({
    model: App.Backbone.Model.Vision
});

App.Backbone.Model.Page = Backbone.Model.extend({
    defaults: {
        pageMode: App.Const.PageMode.EMPTY,
        loggedInUserId: USER['id'],
        currentUserId: USER['id'],
        visionList: new App.Backbone.Model.VisionList(),
        selectedVisions: new App.Backbone.Model.VisionList(),
        otherVisions: new App.Backbone.Model.VisionList(),
        user: null,
    },
    initialize: function() {
    },
    // Getters
    pageMode: function() { return this.get("pageMode"); },
    loggedInUserId: function() { return this.get("loggedInUserId"); },
    currentUserId: function() { return this.get("currentUserId"); },
    visionList: function() { return this.get("visionList"); },
    selectedVisions: function() { return this.get("selectedVisions"); },
    otherVisions: function() { return this.get("otherVisions"); },
    user: function() { return this.get("user"); },
    getSelectedVision: function(visionId) {
        var list = this.selectedVisions().where({id: visionId});
        if (list.length > 0) {
            assert(list.length == 1, "Shouldn't have multiple models here")
            return list[0];
        }
        return null;
    },
    numSelectedVisions: function() {
        return this.selectedVisions().length;
    },
    activeVisionList: function() {
        var pageMode = this.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST ||
            pageMode == App.Const.PageMode.HOME_USER) {
            return this.otherVisions();
        } else if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            return this.selectedVisions();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            if (App.Var.Model.currentUserId() == USER.id) {
                return this.visionList();
            } else {
                return this.otherVisions();
            }
        } else {
            assert(false, "Invalid pageMode");
            return null;
        }
    },

    // Setters
    setPageMode: function(mode) {
        assert(mode > 0 && mode < App.Const.PageMode.INVALID,
               "Invalid page mode");
        // Always trigger view to change
        // This is there because we are using USER_PROFILE mode for
        // different users right now
        this.set({pageMode: mode}, {silent: true});
        this.trigger("change:pageMode");
    },
    setUser: function(user) {
        this.set({ user : new App.Backbone.Model.User(user)});
    },
    setCurrentUserId: function(id) {
        var currentUserId = this.currentUserId();
        assert(id > 0, "Invalid user id");
        this.set({currentUserId: id}, {silent: true});
    },
    setVisionList: function(visionList) {
        // Note: need to use reset so that the methods bound to this collection
        //       still get called
        this.visionList().reset(visionList);
    },
    setOtherVisions: function(visionList) {
        // Note: need to use reset so that the methods bound to this collection
        //       still get called
        this.otherVisions().reset(visionList);
    },
    addToSelectedVisions: function(model) {
        var vision = this.getSelectedVision(model.visionId());
        if (vision == null) {
            // Note that we clone the model. We want our own copy for in
            // case we want to let the user edit it in some way
            this.selectedVisions().push(model.deepClone());
            return true;
        }
        return false;
    },
    removeFromSelectedVisions: function(model) {
        var vision = this.getSelectedVision(model.visionId());
        if (vision != null) {
            this.selectedVisions().remove(vision);
            return true;
        }
        return false;
    },
    inVisionList: function(visionModel) {
        var list = this.visionList().where({id: visionModel.visionId()});
        var rootList = this.visionList().where({rootId: visionModel.rootId()});
        return (list.length > 0) || (rootList.length > 0);
    },
    getVisionInList: function(visionId) {
        var list = this.visionList().where({id: visionId});
        if (list.length > 0) {
            assert(list.length == 1, "Shouldn't have multiple models here")
            return list[0];
        }
        return null;
    },
    getInOtherVisions: function(visionId) {
        var list = this.otherVisions().where({id: visionId});
        if (list.length > 0) {
            assert(list.length == 1, "Shouldn't have multiple models here")
            return list[0];
        }
        return null;
    },
    moveSelectedVision: function(srcIndex, destIndex) {
        // We don't move silently here because we want to trigger
        // and update to the hidden input with the selected visions list
        var list = this.selectedVisions();
        var model = list.at(srcIndex);
        list.remove(model);
        list.add(model, {at: destIndex})
    },
    moveVision: function(srcIndex, destIndex) {
        // Move silently because the UI is already updated upon move
        var list = this.visionList();
        var model = list.at(srcIndex);
        list.remove(model, {silent: true});
        list.add(model, {at: destIndex, silent: true})
    },
    deleteVision: function(visionId) {
        var toRemove = this.getVisionInList(visionId);
        assert(toRemove != null, "Couldn't find vision id to remove");
        this.visionList().remove(toRemove);
    },
    repostVisionDone: function(repostId, newVision) {
        // Add new vision to visionList
        this.visionList().unshift(new App.Backbone.Model.Vision(newVision),
                                  {silent: true});
        // Trigger change in repostId so we re-render it as in the vision list
        var repostModel = this.getInOtherVisions(repostId);
        if (null != repostModel) {
            repostModel.trigger("change");
        }
    },
    addVision: function(newVision) {
        // Add new vision to visionList
        this.visionList().unshift(new App.Backbone.Model.Vision(newVision));
    },
    addVisionComment: function(newComment) {
        // Find vision to add to
        console.log("NEW COMMENT: " + JSON.stringify(newComment));
        var list = this.activeVisionList();
        var vision = null;
        for (var i = 0 ; i < list.length ; i++) {
            if (list.at(i).visionId() == newComment['visionId']) {
                vision = list.at(i);
            }
        }

        // Add comment to vision
        if (null != vision) {
            vision.addComment(newComment);
        }

        // Trigger that height change and we need to re-layout
        this.trigger("new-comment");
    },
});

/******************************************************************************
 * Backbone views
 */

App.Backbone.View.VisionComment = Backbone.View.extend({
    className: "VisionComment",
    initialize: function() {
        _.bindAll(this, "gotoUser");
        this.render();
    },
    events: {
        "click .VisionCommentUserLink" : "gotoUser",
    },
    render: function() {
        var variables = { 'authorId' : this.model.authorId(),
                          'text': this.model.text(),
                          'name': this.model.name(),
                          'picture': this.model.picture()}
        var template = _.template($("#VisionCommentTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
    gotoUser: function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log("GOTO USER");
        App.Var.Router.navigate("/user/" + this.model.authorId(),
                                {trigger: true});
    },
});

App.Backbone.View.VisionDetailsComment = Backbone.View.extend({
    className: "VisionDetailsComment",
    initialize: function() {
        //_.bindAll(this, "gotoUser");
        this.render();
    },
    render: function() {
        var variables = { 'authorId' : this.model.authorId(),
                          'text': this.model.text(),
                          'name': this.model.name(),
                          'picture': this.model.picture()}
        var template = _.template($("#VisionDetailsCommentTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
});

App.Backbone.View.Vision = Backbone.View.extend({
    tagName: "li",
    className: VISION_CLASS,
    initialize: function() {
        _.bindAll(this, "itemSelect", "renderComment",
                        "mouseEnter", "mouseLeave",
                        "repostVision", "removeVision", "gotoUser",
                        "visionCommentInput");
        this.model.bind("change", this.render, this);
        this.model.comments().bind("add", this.render, this);

        this.render();
    },
    //Using variables in events
    //http://stackoverflow.com/questions/8400450/using-variable-for-selectors-in-events
    events: function(){

        var _events = {
            "click .VisionPicture" : "itemSelect",
            "mouseenter" : "mouseEnter", //TODO: Fix
            "mouseleave" : "mouseLeave", //TODO: Fix
            "keyup .AddVisionCommentInput" : "visionCommentInput",
            "click .VisionUserName"        : "gotoUser"
        };

        _events["click " + REPOST_BUTTON] = "repostVision";

        return _events;
    },
    render: function() {
        var pageMode = App.Var.Model.pageMode();

        var selected = false;
        //For the not authenticated
        var removeButtonVisibility = "Hidden";
        if ((pageMode == App.Const.PageMode.HOME_GUEST ||
            (pageMode == App.Const.PageMode.USER_PROFILE && !userLoggedIn())) &&
            this.model.isSelected()) {
            selected = true;
            //Show
            removeButtonVisibility = "";
        }
        var pictureUrl = "";
        if (null != this.model.picture()) {
            pictureUrl = this.model.picture().mediumUrl();
        }

        var addCommentVisibility = "";
        if (!userLoggedIn()) {
            addCommentVisibility = "Hidden";
        }

        //Default Pointer
        var cursorStyleMove = false;
        var moveDisplay = "none";
        var removeDisplay = "none";
        var repostDisplay = "none";
        var mineDisplay = "none";
        var nameDisplay = "none";

        var haveVisionVisibility = "Hidden";

        if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            removeDisplay = "inline-block";

        } else if (pageMode == App.Const.PageMode.HOME_GUEST) {
            nameDisplay = "block";
        } else if (pageMode == App.Const.PageMode.HOME_USER) {
            nameDisplay = "block";
            if (App.Var.Model.inVisionList(this.model)) {
                mineDisplay = "inline-block";
                selected = true;
                haveVisionVisibility = "";
            } else {
                repostDisplay = "inline-block";
            }
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            if (userLoggedIn()) {
                if (App.Var.Model.currentUserId() == USER.id) {
                    moveDisplay = "inline-block";
                } else {
                    if (App.Var.Model.inVisionList(this.model)) {
                        mineDisplay = "inline-block";
                        selectedClass = "MasonryItemSelected";
                        haveVisionVisibility = "";
                    } else {
                        repostDisplay = "inline-block";
                    }
                }
            }
            cursorClass = "MasonryItemPointerCursor";
        }

        //Clean for html (using it in the alt=" attribute of the image so don't want '' or "")
        var text = _.escape(this.model.text());

        //Selected
        if(selected) $(this.el).addClass(VISION_SELECTED_CLASS);

        //Cursor
        //TODO: Figure out how to design move

        var variables = {text : text,
                         pictureUrl: pictureUrl,
                         moveDisplay: moveDisplay,
                         removeDisplay: removeDisplay,
                         repostDisplay: repostDisplay,
                         mineDisplay: mineDisplay,
                         removeButtonVisibility: removeButtonVisibility,
                         addCommentVisibility: addCommentVisibility,
                         haveVisionVisibility: haveVisionVisibility,
                         name: this.model.name(),
                         nameDisplay: nameDisplay,
                         userId: this.model.userId(),
                         profile: USER['picture'],
                        };

        var template = _.template($("#VisionTemplate").html(), variables);
        $(this.el).html(template);

        // render last 4 comments
        this.comments = []
        var commentList = this.model.comments().last(4);
        for (var i = 0 ; i < commentList.length ; i++) {
            this.renderComment(commentList[i], i);
        }
        $(this.el).find(VISION_COMMENT_CONTAINER).append(this.comments);

        return this;
    },
    renderComment: function(comment, index) {
        if (comment.visionCommentId() > 0) {
            var c = new App.Backbone.View.VisionComment({ model: comment });
            this.comments.push(c.el);
        }
    },
    itemSelect: function(e) {
        var pageMode = App.Var.Model.pageMode();
        if (pageMode == App.Const.PageMode.HOME_GUEST ||
            (pageMode == App.Const.PageMode.USER_PROFILE && !userLoggedIn())) {
            this.model.toggleSelected();
            this.mouseEnter();
        } else if (pageMode != App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            App.Var.View.showVisionDetails(this.model);
        }
    },
    
    showElement: function(selector) {
        $(this.el).find(selector).fadeIn(ANIMATION_TIME);
    },

    hideElement: function(selector) {

        //Get element
        var element =  $(this.el).find(selector);

        //Hide
        if(element.is(":visible"))
            element.fadeOut(ANIMATION_TIME);
    },

    mouseEnter: function() {
        
        //Get the current state
        var pageMode = App.Var.Model.pageMode();

        //If we are on the main page
        // AND the user is not logged in
        // AND vision is not selected
        if (pageMode == App.Const.PageMode.HOME_GUEST ||
            (pageMode == App.Const.PageMode.USER_PROFILE && !userLoggedIn())) {
            if(!this.model.isSelected()) {
                this.showElement(ADD_NOT_LOGGED_IN_VISION_SELECTOR);  
            }
        } else if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            // don't show anything
        } else {
            //Repost
            if(!App.Var.Model.inVisionList(this.model)) {
                this.showElement(REPOST_BUTTON);
            }
        }
        //TODO: Add the case when they come to another persons page
        // AND they are not logge din
        // Show the instructions bar (box)  

        //On your own board show move butotn!
        if (pageMode == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.currentUserId() == USER.id) {
            this.showElement(MOVE_ICON);
        }

        //Vision Overlay

    },
    mouseLeave: function() {
        
        //Get current state
        var pageMode = App.Var.Model.pageMode();

        //Get all of the possible overlays
        var buttons = [ADD_NOT_LOGGED_IN_VISION_SELECTOR, REPOST_BUTTON, MOVE_ICON];
        
        //If a overlay / button is showing, hide it
        for (var i = 0 ; i < buttons.length ; i++) {
            this.hideElement(buttons[i]);
        }

    },
    repostVision: function(e) {
        e.preventDefault();
        App.Var.View.repostVision(this.model);
    },
    removeVision: function(e) {
        e.preventDefault();
        if (App.Var.Model.pageMode() == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            App.Var.Model.removeFromSelectedVisions(this.model);
        } else {
            assert(false, "Should be in test vision page");
        }
    },
    gotoUser: function(e) {
        e.stopPropagation();    // prevent propagating to other handlers
        e.preventDefault();     // prevent following link
        App.Var.Router.navigate("/user/" + this.model.userId(),
                                {trigger: true});
    },
    visionCommentInput: function(e) {
        if(e.keyCode == 13) {
            var text = $.trim($(this.el).find(".AddVisionCommentInput").val());
            if (text.length > 0) {
                App.Var.View.addVisionComment(this.model.visionId(), text);
            }
        }
    },
});

App.Backbone.View.Page = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, "masonryReload",
                        "showVisionDetails",
                        "hideVisionDetails",
                        "ajaxVisionDetailsCommentsSuccess",
                        "ajaxVisionDetailsCommentsError",
                        "toggleVisionDetailsEditSubmit",
                        "visionDetailsEditSubmit",
                        "ajaxVisionDetailsEditSuccess",
                        "ajaxVisionDetailsEditError",
                        "renderVisionDetailsComments",
                        "renderVisionDetailsComment",
                        "deleteVision",
                        "ajaxDeleteVisionSuccess",
                        "ajaxDeleteVisionError",
                        "repostVision",
                        "ajaxRepostVisionSuccess",
                        "ajaxRepostVisionError",
                        "addVisionComment",
                        "ajaxAddVisionCommentSuccess",
                        "ajaxAddVisionCommentError",
                        // Changing page mode and rendering rest of page
                        "changePageMode",
                        "showInfoBar",
                        "hideInfoBar",
                        // For onboarding
                        "showAddItemButton",
                        "hideAddItemButton",
                        "changeInSelectedVisions",
                        "selectedVisionsSortStart",
                        "selectedVisionsSortChange",
                        "selectedVisionsSortStop",
                        "renderExampleVisionBoard",
                        "renderSelectedVision",
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
                        "setUserDescription");
        this.model.bind("change:pageMode", this.changePageMode, this);
        this.model.otherVisions().bind("reset", 
                                       this.renderVisionList,
                                       this);
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
        this.model.bind("new-comment", this.masonryReload, this);
        // initialize a few variables
        this.selectedVisionMoveIndex = -1;
        this.srcIndex = -1;
        this.currentVision = null;
    },
    currentVisionEditable: function() {
        return userLoggedIn() && this.currentVision.userId() == USER['id'];
    },
    repostVision: function(visionModel) {
        assert(visionModel != null, "Vision model to repost is null");
        if (visionModel != null) {
            console.log("REPOST: " + visionModel.visionId());
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

    addVisionComment: function(visionId, text) {
        console.log("VISION " + visionId + " : " + text);

        doAjax("/api/vision/" + visionId + "/add_comment",
                JSON.stringify({
                                'visionId' : visionId,
                                'text' : text,
                                }),
                this.ajaxAddVisionCommentSuccess,
                this.ajaxAddVisionCommentError
        );
    },
    ajaxAddVisionCommentSuccess: function(data, textStatus, jqXHR) {
        this.model.addVisionComment(data.newComment);

        // TODO: this is kind of a hack for now, but it only renders if the
        //       details modal is displayed so it works.  Later we really want
        //       a way where the add event from the comment list triggers a
        //       re-render
        this.renderVisionDetailsComments();
    },
    ajaxAddVisionCommentError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    showVisionDetails: function(visionModel) {
        this.currentVision = visionModel;

        // Note: jQuery text() method escapes html brackets and stuff
        var modal = $(VISION_DETAILS_MODAL).first();

        modal.find(VISION_DETAILS_NAME).text(this.currentVision.name());
        modal.find(VISION_DETAILS_PICTURE).attr("src",
                                     this.currentVision.picture().largeUrl());
        modal.find(VISION_DETAILS_TEXT).text(this.currentVision.text());
        modal.find(VISION_DETAILS_ADD_COMMENT_PICTURE).attr("src",
                                                           USER['picture']);
        modal.find(VISION_DETAILS_COMMENTS_CONTAINER).empty().hide();
        
        if (userLoggedIn()) {
            $(VISION_DETAILS_ADD_COMMENT_CONTAINER).show();
        } else {
            $(VISION_DETAILS_ADD_COMMENT_CONTAINER).hide();
        }

        if (userLoggedIn() &&
            App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.loggedInUserId() == App.Var.Model.currentUserId()) {
            $(VISION_DELETE_BUTTON).show();
        } else {
            $(VISION_DELETE_BUTTON).hide();
        }

        // Edit info form
        $("#VisionDetailsTextInput").val(this.currentVision.text());
        if (this.currentVision.isPublic()) {
            $("#VisionDetailsPrivacyInput").prop("checked", "checked");
        } else {
            $("#VisionDetailsPrivacyInput").removeProp("checked");
        }
        this.toggleVisionDetailsEditSubmit();
        $(VISION_DETAILS_EDIT_FORM).hide();
        $(VISION_DETAILS_TEXT_CONTAINER).show();

        $("body").addClass("NoScroll");
        modal.fadeIn("slow");

        doAjax("/api/vision/" + this.currentVision.visionId() + "/comments",
                JSON.stringify({
                                'visionId' : this.currentVision.visionId(),
                                }),
                this.ajaxVisionDetailsCommentsSuccess,
                this.ajaxVisionDetailsCommentsError
        );
    },
    hideVisionDetails: function() {
        var modal = $(VISION_DETAILS_MODAL).first().fadeOut("fast");
        $("body").removeClass("NoScroll");
    },
    ajaxVisionDetailsCommentsSuccess: function(data, textStatus, jqXHR) {
        this.currentVision.setComments(data.comments);
        this.renderVisionDetailsComments();
    },
    ajaxVisionDetailsCommentsError: function(jqXHR, textStatus, errorThrown) {
        // do nothing
        $(VISION_DETAILS_COMMENTS_CONTAINER).show();
    },
    renderVisionDetailsComments: function() {
        if (this.currentVision != null) {
            console.log("Render comments in vision details.");
            var container = $(VISION_DETAILS_COMMENTS_CONTAINER).first();
            container.empty();
            var commentList = this.currentVision.comments();
            if (commentList.length > 0) {
                this.comments = [];
                commentList.each(this.renderVisionDetailsComment);
                container.show();
                container.append(this.comments);

                // These few lines are a total hack to get the scroll to
                // work. I tried lots of tricks/hacks with scrollHeight but
                // nothing worked across browsers better than this so far.
                container.animate({scrollTop: "1000000px"});

                this.comments = [];
            }
            $(VISION_DETAILS_ADD_COMMENT).val("");
        }
    },
    renderVisionDetailsComment: function(comment, index) {
        if (comment.visionCommentId() > 0) {
            var c = new App.Backbone.View.VisionDetailsComment(
                                                            { model: comment });
            this.comments.push(c.el);
        }
    },
    toggleVisionDetailsEditSubmit: function(e) {
        var text = $.trim($("#VisionDetailsTextInput").val());
        var textLength = text.length;
        var isPublic = $("#VisionDetailsPrivacyInput").is(":checked");
        var change = false;
        var invalid = false;
        if (text != this.currentVision.text()) {
            change = true;
            if (textLength <= 0) {
                invalid = true;
            }
        }
        if (isPublic != this.currentVision.isPublic()) {
            change = true;
        }
        if (true == change && false == invalid) {
            $("#VisionDetailsEditSubmit").removeAttr("disabled");
        } else {
            $("#VisionDetailsEditSubmit").attr("disabled", "disabled");
        }
    },
    visionDetailsEditSubmit: function() {
        assert (this.currentVision != null, "Invalid current vision");

        console.log("EDIT");
        var text = $.trim($("#VisionDetailsTextInput").val());
        var isPublic = $("#VisionDetailsPrivacyInput").is(":checked");

        doAjax("/api/vision/" + this.currentVision.visionId() + "/edit",
                JSON.stringify({
                                'visionId' : this.currentVision.visionId(),
                                'text'     : text,
                                'isPublic' : isPublic,
                                }),
                this.ajaxVisionDetailsEditSuccess,
                this.ajaxVisionDetailsEditError
              );
    },
    ajaxVisionDetailsEditSuccess: function(data, textStatus, jqXHR) {
        if (this.currentVision) {
            this.currentVision.edit(data.text, data.isPublic);
            $(VISION_DETAILS_TEXT).html(data.text);
            this.toggleVisionDetailsEditSubmit();
            $(VISION_DETAILS_EDIT_FORM).hide();
            $(VISION_DETAILS_TEXT_CONTAINER).show();
        }
    },
    ajaxVisionDetailsEditError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    deleteVision: function() {
        if (this.currentVision != null) {
            console.log("DELETE");
            doAjax("/api/user/" + USER['id'] + "/delete_vision",
                   JSON.stringify({
                                    'visionId' : this.currentVision.visionId(),
                                  }),
                   this.ajaxDeleteVisionSuccess,
                   this.ajaxDeleteVisionError
            );
        }
    },
    ajaxDeleteVisionSuccess: function(data, textStatus, jqXHR) {
        console.log("REMOVED ID: " + data.removedId);
        this.model.deleteVision(data.removedId);

        this.hideVisionDetails();
    },
    ajaxDeleteVisionError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    /*
     * Changing page mode triggered by set of this.model.pageMode
     */
    changePageMode: function() {
        console.log("CHANGE MODE: " + this.model.pageMode());

        var pageMode = this.model.pageMode();

        if (pageMode == App.Const.PageMode.HOME_GUEST) {
            this.showInfoBar(true);
            this.hideAddItemButton();
            this.showHome();
        } else if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            this.showInfoBar(false);
            this.showExampleVisionBoard();
        } else if (pageMode == App.Const.PageMode.HOME_USER) {
            this.hideInfoBar();
            this.hideAddItemButton();
            this.showHome();
        } else if (pageMode == App.Const.PageMode.USER_PROFILE) {
            if (userLoggedIn()) {
                this.hideInfoBar();
                this.showAddItemButton();
            } else {
                this.showInfoBar(true);
                this.hideAddItemButton();
            }
            this.showProfile();
        } else {
            assert(false, "Invalid page mode in changePageMode");
        }
    },

    /*
     * Render vision list: triggered by set of this.model.visionList
     */
    renderVisionList: function() {
        
        if(DEBUG) console.log("rendering vision list");

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
        var vision = new App.Backbone.View.Vision({ model: vision });
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
        var vision = new App.Backbone.View.Vision({ model: vision });
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
            $(INSTRUCTIONS_DIV).show();
            $(INSTRUCTIONS_PADDING).show();
        } else {
            $(INSTRUCTIONS_DIV).hide();
            $(EXAMPLE_VISION_BOARD_INSTRUCTIONS).show();
            $(INSTRUCTIONS_PADDING).show();
        }
    },
    hideInfoBar: function() {
        $(INSTRUCTIONS_PADDING).hide();
        $(INSTRUCTIONS_DIV).hide();
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
        if (length >=0 && length <= NUM_VISION_REQUIRED_FOR_USER) 
            this.hideAllExcept(instructions,length);

        //User has selected more
        else if(length > NUM_VISION_REQUIRED_FOR_USER)
            this.hideAllExcept(instructions, NUM_VISION_REQUIRED_FOR_USER);

        //Should never have < 0 visions selected!
        else
            console.log("ERROR - should not have negative count visions!");



        // Update hidden field in registration
        var visionIds = [];
        for (var i = 0 ; i < length ; i++) {
            visionIds.push(this.model.selectedVisions().at(i).visionId());
        }
        $(USER_SELECTED_VISIONS_INPUT).first().attr("value", JSON.stringify(visionIds));
        console.log("VISION LIST: " + JSON.stringify(visionIds));

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
                elements[i].show();//(CSS_ClASS_HIDDEN);
            } else {
                elements[i].hide();//addClass(CSS_ClASS_HIDDEN);
            }
        }
    },
    /*
     * Render home page
     */
    showHome: function() {
        this.hideUserInformation();
        $(EXAMPLE_VISION_BOARD_DIV).empty().hide();
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
        console.log("Render Home");
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

        /*
        var variables = {};
        var template = _.template($("#HomePageLoadErrorTemplate").html(),
                                  variables);
        $(LOADING_INDICATOR_DIV).html(template).show();
        */
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
        console.log("Rendering Profile");

        this.model.setVisionList(App.Var.JSON.visionList);
        if (App.Var.Model.currentUserId() != USER.id) {
            this.model.setOtherVisions(App.Var.JSON.otherVisions);
        }
        this.model.setUser(App.Var.JSON.user);
    },
    renderProfileError: function() {
        var masonryContainer = $(CONTENT_DIV).first();
        masonryContainer.empty().masonry();

        /*
        var variables = {};
        var template = _.template($("#ProfileLoadErrorTemplate").html(),
                                  variables);
        $(LOADING_INDICATOR_DIV).html(template).show();
        */
    },
    showUserInformation: function() {
        console.log("SET USER INFO");
        $("#UserName").html(this.model.user().fullName());
        var desc = this.model.user().description();
        if (desc == "") {
            if (this.model.user().userId() == USER.id) {
                $("#NoUserDescription").show();
                $("#UserDescription").empty().hide();
            } else {
                $("#NoUserDescription").hide();
                $("#UserDescription").empty().show();
            }
        } else {
            $("#NoUserDescription").hide();
            $("#UserDescription").html(desc);
        }
        $("#SetUserDescriptionContainer").hide();

        $("#UserProfilePicture").attr("src", this.model.user().picture());
        $("#UserInformation").show();
    },
    hideUserInformation: function() {
        $("#UserInformation").hide();
    },
    setUserDescription: function(description) {
        if (description.length > 0 &&
            App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.loggedInUserId() == App.Var.Model.currentUserId()) {

            $("#NoUserDescription").hide();
            $("#SetUserDescriptionContainer").hide();
            $("#UserDescription").html(description);
        }
    },
});

/******************************************************************************
 * Router
 */
App.Backbone.Router = Backbone.Router.extend({
  routes: {
    ""                : "home",
    "user/:userId"    : "profile",
    "view_board"      : "viewBoard",
    "*action"         : "home",
  },
  home: function() {
    if (userLoggedIn()) {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_USER);
    } else {
        App.Var.Model.setPageMode(App.Const.PageMode.HOME_GUEST);
    }
  },
  viewBoard: function() {
      if (!userLoggedIn() &&
          (App.Var.Model.pageMode() == App.Const.PageMode.HOME_GUEST ||
           App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE)) {
        App.Var.Model.setPageMode(App.Const.PageMode.EXAMPLE_VISION_BOARD);
      } else {
        assert(false, "Shouldn't be logged in or come from another page");
      }
  },
  profile: function(userId) {
    App.Var.Model.setCurrentUserId(userId);
    App.Var.Model.setPageMode(App.Const.PageMode.USER_PROFILE);
  },
});
App.Var.Router = new App.Backbone.Router();

/******************************************************************************
 * Document ready
 */
$(document).ready(function() {
    $.ajaxSetup({ cache: false});

    App.Var.Model = new App.Backbone.Model.Page();
    App.Var.View = new App.Backbone.View.Page({model: App.Var.Model});

    // Do this after we have created Page model and view
    Backbone.history.start({pushState: true});

    $("#NavHome").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/", {trigger: true});
    });
    $("#BackToMainPageButton").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/", {trigger: true});
    });
    $("#NavProfile").click(function(e) {
        e.preventDefault();
        App.Var.Router.navigate("/user/" + USER['id'], {trigger: true});
    });

    $(VIEW_EXAMPLE_VISION_BOARD_BUTTON).click(function(e) {
        e.preventDefault();
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
    $(JOIN_SITE_BUTTON).click(function() {
        $(REGISTER_FORM).first().submit();
    });

    $("#VisionDeleteButton").click(function() {
        App.Var.View.deleteVision();
    });

    /*
     * File upload stuff
     */
    function toggleAddVisionSubmit() {
        var enable = false;
        var fileName = $("#FileUploadInput").val();
        if (fileName != "") {
            enable = true;
        }
        /* Should we allow text w/o image?
        var text = $.trim($("#InputText").val());
        if (text != "") {
            console.log("TEXT: " + text);
            enable = true;
        }
        */
        if (enable == true) {
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
        if (USER['visionPrivacy'] == true) {
            $("#InputVisionPrivacy").prop("checked", "checked");
        } else {
            $("#InputVisionPrivacy").removeProp("checked");
        }
    });
    $("#FileUploadInput").change(function() {
        var fileName = $("#FileUploadInput").val();
        if (fileName != "") {
            // Show user we are processing file
            console.log("UPLOAD: " + fileName);

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

        console.log("File uploaded!");
        var jsonText = $("#FileUploadTarget").contents().find("body").html();
        var result  = eval('(' + jsonText+ ')');
        if (result && result.result == "success") {
            // Show image uploaded
            console.log("url: " + result.url);
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
            console.log("UPLOAD ERROR");
            $("#FileUploadInvalid").show();
            $("#FileUploadNoPreview").hide();
            $("#FileUploadLoading").hide();
            $("#FileUploadImageContainer").hide();
            $("#FileUploadInput").val("");
        }
        toggleAddVisionSubmit();
    });
    /*
    $("#InputText").keyup(toggleAddVisionSubmit);
    $("#InputText").bind('paste',toggleAddVisionSubmit);
    $("#InputText").bind('cut',toggleAddVisionSubmit);
    */
    $("#AddVisionSubmit").click(function() {
        var useImage = false;
        if ($("#FileUploadInput").val() != "") {
            useImage = true;
        }

        var text = $.trim($("#InputText").val());
        var visionPrivacy = $("#InputVisionPrivacy").is(":checked");

        doAjax("/api/user/" + USER['id'] + "/add_vision",
                JSON.stringify({'useImage' : useImage,
                                'text' : text,
                                'privacy' : visionPrivacy }),
                // success
                function(data, textStatus, jqXHR) {
                    console.log("Success: " + JSON.stringify(data));
                    App.Var.Model.addVision(data.newVision);
                    $("#AddVisionModal").modal("hide");
                },
                // error
                function(jqXHR, textStatus, errorThrown) {
                    console.log("Error");
                }
        );
    });

    $(VISION_DETAILS_ADD_COMMENT).keydown(function(e) {
        if(e.keyCode == 13) {
            e.preventDefault();
            var text = $.trim($(VISION_DETAILS_ADD_COMMENT).val());
            if (text.length > 0) {
                App.Var.View.addVisionComment(
                            App.Var.View.currentVision.visionId(),
                            text);
            }
        }

    });
    $(VISION_DETAILS_TEXT_CONTAINER).mouseenter(function() {
        if (App.Var.View.currentVisionEditable()) {
            $(VISION_DETAILS_EDIT_TEXT).show();
        }
    });
    $(VISION_DETAILS_TEXT_CONTAINER).mouseleave(function() {
        if (App.Var.View.currentVisionEditable()) {
            $(VISION_DETAILS_EDIT_TEXT).hide();
        }
    });
    $(VISION_DETAILS_EDIT_TEXT).click(function() {
        if (App.Var.View.currentVisionEditable()) {
            $(VISION_DETAILS_TEXT_CONTAINER).hide();
            $(VISION_DETAILS_EDIT_FORM).show();
        }
    });
    $("#VisionDetailsPrivacyInput").change(App.Var.View.toggleVisionDetailsEditSubmit);
    $("#VisionDetailsTextInput").keyup(App.Var.View.toggleVisionDetailsEditSubmit);
    $("#VisionDetailsTextInput").bind("cut", App.Var.View.toggleVisionDetailsEditSubmit);
    $("#VisionDetailsTextInput").bind("paste", App.Var.View.toggleVisionDetailsEditSubmit);

    $("#VisionDetailsEditSubmit").click(App.Var.View.visionDetailsEditSubmit);

    // Catch cases for closing the vision details modal
    // This is if we click on the close button, or we click on the
    // modal, but not on the inner box.
    $(VISION_DETAILS_MODAL_BOX).click(function(e) {
        e.stopPropagation();
    });
    $(VISION_DETAILS_MODAL).click(App.Var.View.hideVisionDetails);
    $(VISION_DETAILS_CLOSE).click(App.Var.View.hideVisionDetails);

    /*
     * For entering user description in user info box
     */
    function countUserDescriptionChars() {
        var desc = $.trim($("#UserDescriptionInput").val());
        var lengthLeft = MAX_USER_DESCRIPTION_LENGTH - desc.length;

        if (lengthLeft >= 0) {
            $("#UserDescriptionSubmit").removeAttr("disabled");
        } else {
            $("#UserDescriptionSubmit").attr("disabled", "disabled");
        }
        $("#UserDescriptionLength").html(lengthLeft);
    }
    $("#NoUserDescription").mouseenter(function(e) {
        $(this).removeClass("NoUserDescriptionNotActive");
        $(this).addClass("NoUserDescriptionActive");
    });
    $("#NoUserDescription").mouseleave(function(e) {
        $(this).removeClass("NoUserDescriptionActive");
        $(this).addClass("NoUserDescriptionNotActive");
    });
    $("#NoUserDescription").click(function(e) {
        $(this).hide();
        $("#SetUserDescriptionContainer").show();
        $("#UserDescriptionInput").text("").focus();
        countUserDescriptionChars();
    });
    $("#UserDescriptionInput").keyup(countUserDescriptionChars)
    $("#UserDescriptionInput").bind('paste', countUserDescriptionChars);
    $("#UserDescriptionInput").bind('cut', countUserDescriptionChars);
    $("#UserDescriptionSubmit").click(function() {
        console.log("SUBMIT DESC");
        var desc = $.trim($("#UserDescriptionInput").val());
        doAjax("/api/user/" + USER['id'] + "/set_description",
                JSON.stringify({'description' : desc }),
                // success
                function(data, textStatus, jqXHR) {
                    App.Var.View.setUserDescription(data.description);
                },
                // error
                function(jqXHR, textStatus, errorThrown) {
                    console.log("Error");
                }
        );
    });
});
/* $eof */
