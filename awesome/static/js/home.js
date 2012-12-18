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

var VISION_DETAILS_MODAL = "#VisionDetailsModal";

var USER_INFORMATION = "#UserInformation";

var VISION_CLASS = "Vision";
var VISION_CLASS_SELECTOR = "." + VISION_CLASS;

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

//Utility
var CSS_CLASS_HIDDEN = "CSS_CLASS_HIDDEN";


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
        if (DEBUG) console.log("NEW COMMENT: " + JSON.stringify(newComment));
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
        if (DEBUG) console.log("GOTO USER");
        App.Var.Router.navigate("/user/" + this.model.authorId(),
                                {trigger: true});
    },
});

App.Backbone.View.UserInformation = Backbone.View.extend({
    tagName: "div",
    sel: {
        SET_DESCRIPTION: "#SetUserDescriptionContainer",
        INPUT : "#UserDescriptionInput",
        SUBMIT : "#UserDescriptionSubmit",
        LENGTH: "#UserDescriptionLength",
        DESCRIPTION : "#UserDescription",
        NO_DESCRIPTION : "#NoUserDescription",
    },
    constant: {
        MAX_USER_DESCRIPTION_LENGTH : 200,
    },
    initialize: function() {
        _.bindAll(this, "countDesc", "onMouseEnter", "onMouseLeave", "onClick",
                        "submitDesc", "setUserDescription");
        this.render();
    },
    events: function() {
        var _events = {};
        _events["mouseenter " + this.sel.NO_DESCRIPTION] = "onMouseEnter";
        _events["mouseleave " + this.sel.NO_DESCRIPTION] = "onMouseLeave";
        _events["click " + this.sel.NO_DESCRIPTION] = "onClick";
        _events["keyup " + this.sel.INPUT] = "countDesc";
        _events["cut " + this.sel.INPUT] = "countDesc";
        _events["paste " + this.sel.INPUT] = "countDesc";
        _events["click " + this.sel.SUBMIT] = "submitDesc";
        return _events;
    },
    render: function() {
        var desc = this.model.description();
        var descDisplay = "";
        var noDescDisplay = "hide";
        if (desc == "" && this.model.userId() == USER.id) {
            descDisplay = "hide";
            noDescDisplay = "";
        }

        var variables = { 
            name: this.model.fullName(),
            desc: desc,
            descDisplay: descDisplay,
            noDescDisplay: noDescDisplay,
            picture: this.model.picture(),
        };
        var template = _.template($("#UserInformationTemplate").html(),
                                  variables);
        $(this.el).html(template);

        return this;
    },
    onMouseEnter: function() {
        $(this.el).find(this.sel.NO_DESCRIPTION).removeClass("NoUserDescriptionNotActive");
        $(this.el).find(this.sel.NO_DESCRIPTION).addClass("NoUserDescriptionActive");
    },
    onMouseLeave: function() {
        $(this.el).find(this.sel.NO_DESCRIPTION).removeClass("NoUserDescriptionActive");
        $(this.el).find(this.sel.NO_DESCRIPTION).addClass("NoUserDescriptionNotActive");
    },
    onClick: function() {
        $(this.el).find(this.sel.NO_DESCRIPTION).hide();
        $(this.el).find(this.sel.SET_DESCRIPTION).show();
        $(this.el).find(this.sel.INPUT).text("").focus();
        this.countDesc();
    },
    countDesc: function() {
        var desc = $.trim($(this.el).find(this.sel.INPUT).val());
        var left = this.constant.MAX_USER_DESCRIPTION_LENGTH - desc.length;

        if (left >= 0) {
            $(this.el).find(this.sel.SUBMIT).removeAttr("disabled");
        } else {
            $(this.el).find(this.sel.SUBMIT).attr("disabled", "disabled");
        }
        $(this.el).find(this.sel.LENGTH).html(left);
    },
    submitDesc: function() {
        if (DEBUG) console.log("SUBMIT DESC");
        var desc = $.trim($(this.sel.INPUT).val());
        doAjax("/api/user/" + USER['id'] + "/set_description",
                JSON.stringify({'description' : desc }),
                // success
                this.setUserDescription,
                // error
                function(jqXHR, textStatus, errorThrown) {
                    console.log("Error");
                }
        );
    },
    setUserDescription: function(data, textStatus, jqXHR) {
        var description = data.description;
        if (description.length > 0 &&
            App.Var.Model.pageMode() == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.loggedInUserId() == App.Var.Model.currentUserId()) {
            $(this.el).find(this.sel.NO_DESCRIPTION).hide();
            $(this.el).find(this.sel.SET_DESCRIPTION).hide();
            $(this.el).find(this.sel.DESCRIPTION).html(description).show();
        }
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

App.Backbone.View.VisionDetailsModal = Backbone.View.extend({
    tagName: "div",
    sel: {
        COMMENTS_CONTAINER : "#VisionDetailsCommentsContainer",
        ADD_COMMENT : "#VisionDetailsAddComment",
        TEXT_CONTAINER : "#VisionDetailsTextContainer",
        EDIT_TEXT : "#VisionDetailsEditText",
        EDIT_FORM : "#VisionDetailsEditForm",
        TEXT : "#VisionDetailsText",
        MODAL_BOX : "#VisionDetailsModalBox",
        CLOSE : "#VisionDetailsClose",
        TEXT_INPUT : "#VisionDetailsTextInput",
        PRIVACY_INPUT : "#VisionDetailsPrivacyInput",
        EDIT_SUBMIT : "#VisionDetailsEditSubmit",
        DELETE_BUTTON : "#VisionDeleteButton",
    },
    initialize: function() {
        _.bindAll(this, "toggleEditSubmit",
                        "ajaxCommentsSuccess",
                        "ajaxCommentsError",
                        "renderComments",
                        "renderComment",
                        "editSubmit",
                        "ajaxEditSuccess",
                        "ajaxEditError",
                        "deleteVision",
                        "ajaxDeleteVisionSuccess",
                        "ajaxDeleteVisionError",
                        "onAddCommentKeydown",
                        "currentVisionEditable",
                        "onTextMouseEnter",
                        "onTextMouseLeave",
                        "onEditClick",
                        "ignoreClick",
                        "closeModal"
        );
        //this.model.bind("change", this.render, this);
        //this.model.comments().bind("add", this.render, this);
        this.render();
    },
    events: function(){
        var _events = {
            "click" : "closeModal",
        };
        _events["click " + this.sel.EDIT_SUBMIT] = "editSubmit";

        _events["click " + this.sel.DELETE_BUTTON] = "deleteVision";
        _events["keydown " + this.sel.ADD_COMMENT] = "onAddCommentKeydown";
        _events["mouseenter " + this.sel.TEXT_CONTAINER] = "onTextMouseEnter";
        _events["mouseleave " + this.sel.TEXT_CONTAINER] = "onTextMouseLeave";
        _events["click " + this.sel.EDIT_TEXT] = "onEditClick";

        _events["change " + this.sel.PRIVACY_INPUT] = "toggleEditSubmit";
        _events["keyup " + this.sel.TEXT_INPUT] = "toggleEditSubmit";
        _events["cut " + this.sel.TEXT_INPUT] = "toggleEditSubmit";
        _events["paste " + this.sel.TEXT_INPUT] = "toggleEditSubmit";
        // Used to ignore clicks to modal box. On others, we close modal
        _events["click " + this.sel.MODAL_BOX] = "ignoreClick";
        _events["click " + this.sel.CLOSE] = "closeModal";

        return _events;
    },
    render: function() {
        var pageMode = App.Var.Model.pageMode();

        var addCommentVisibility = "hide";
        var deleteVisibility = "hide";
        var isPublic = "";
        if (userLoggedIn()) {
            addCommentVisibility = "";

            if (pageMode == App.Const.PageMode.USER_PROFILE &&
                App.Var.Model.loggedInUserId() ==
                    App.Var.Model.currentUserId()) {
                deleteVisibility = "";
            }
            if (this.model.isPublic()) {    
                isPublic = "checked";
            };
        }
        var variables = {
            name : this.model.name(),
            picture : this.model.picture().largeUrl(),
            text : this.model.text(),
            userPicture : USER['picture'],
            addCommentVisibility: addCommentVisibility,
            deleteVisibility: deleteVisibility,
            isPublic: isPublic,
        }
        var template = _.template($("#VisionDetailsModalTemplate").html(),
                                  variables);
        $(this.el).html(template);

        this.toggleEditSubmit();

        doAjax("/api/vision/" + this.model.visionId() + "/comments",
                JSON.stringify({
                                'visionId' : this.model.visionId(),
                                }),
                this.ajaxCommentsSuccess,
                this.ajaxCommentsError
        );
        return this;
    },

    toggleEditSubmit: function(e) {
        var text = $.trim($(this.el).find(this.sel.TEXT_INPUT).val());
        var textLength = text.length;
        var isPublic = $(this.el).find(this.sel.PRIVACY_INPUT).is(":checked");
        var change = false;
        var invalid = false;
        if (text != this.model.text()) {
            change = true;
            if (textLength <= 0) {
                invalid = true;
            }
        }
        if (isPublic != this.model.isPublic()) {
            change = true;
        }
        if (true == change && false == invalid) {
            $(this.el).find(this.sel.EDIT_SUBMIT).removeAttr("disabled");
        } else {
            $(this.el).find(this.sel.EDIT_SUBMIT).attr("disabled", "disabled");
        }
    },

    ajaxCommentsSuccess: function(data, textStatus, jqXHR) {
        this.model.setComments(data.comments);
        this.renderComments();
    },
    ajaxCommentsError: function(jqXHR, textStatus, errorThrown) {
        // still show comment container
        $(this.el).find(this.sel.COMMENTS_CONTAINER).show();
    },
    renderComments: function() {
        if (this.model != null) {
            if (DEBUG) console.log("Render comments in vision details.");
            var container = $(this.el).find(this.sel.COMMENTS_CONTAINER).first();
            container.empty();
            var commentList = this.model.comments();
            if (commentList.length > 0) {
                this.comments = [];
                commentList.each(this.renderComment);
                container.show();
                container.append(this.comments);

                // These few lines are a total hack to get the scroll to
                // work. I tried lots of tricks/hacks with scrollHeight but
                // nothing worked across browsers better than this so far.
                container.animate({scrollTop: "1000000px"});

                this.comments = [];
            }
            $(this.el).find(this.sel.ADD_COMMENT).val("");
        }
    },
    renderComment: function(comment, index) {
        if (comment.visionCommentId() > 0) {
            var c = new App.Backbone.View.VisionDetailsComment(
                                                            { model: comment });
            this.comments.push(c.el);
        }
    },
    editSubmit: function() {
        assert (this.model != null, "Invalid current vision");

        if (DEBUG) console.log("EDIT");
        var text = $.trim($(this.el).find(this.sel.TEXT_INPUT).val());
        var isPublic = $(this.el).find(this.sel.PRIVACY_INPUT).is(":checked");

        doAjax("/api/vision/" + this.model.visionId() + "/edit",
                JSON.stringify({
                                'visionId' : this.model.visionId(),
                                'text'     : text,
                                'isPublic' : isPublic,
                                }),
                this.ajaxEditSuccess,
                this.ajaxEditError
              );
    },
    ajaxEditSuccess: function(data, textStatus, jqXHR) {
        if (this.model) {
            this.model.edit(data.text, data.isPublic);
            $(this.el).find(this.sel.TEXT).html(data.text);
            this.toggleEditSubmit();
            $(this.el).find(this.sel.EDIT_FORM).hide();
            $(this.el).find(this.sel.TEXT_CONTAINER).show();
        }
    },
    ajaxEditError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    deleteVision: function() {
        if (this.model!= null) {
            if (DEBUG) console.log("DELETE");
            doAjax("/api/user/" + USER['id'] + "/delete_vision",
                   JSON.stringify({
                                    'visionId' : this.model.visionId(),
                                  }),
                   this.ajaxDeleteVisionSuccess,
                   this.ajaxDeleteVisionError
            );
        }
    },
    ajaxDeleteVisionSuccess: function(data, textStatus, jqXHR) {
        if (DEBUG) console.log("REMOVED ID: " + data.removedId);
        App.Var.Model.deleteVision(data.removedId);
        App.Var.View.hideVisionDetails();
    },
    ajaxDeleteVisionError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },
    ignoreClick: function(e) {
        e.stopPropagation();
    },
    closeModal: function(e) {
        App.Var.View.hideVisionDetails();
    },

    onAddCommentKeydown: function(e) {
        if(e.keyCode == 13) {
            e.preventDefault();
            var text = $.trim($(this.sel.ADD_COMMENT).val());
            if (text.length > 0) {
                App.Var.View.addVisionComment(
                            App.Var.View.currentVision.visionId(),
                            text);
            }
        }

    },
    currentVisionEditable: function() {
        return userLoggedIn() && this.model.userId() == USER['id'];
    },
    onTextMouseEnter: function() {
        if (this.currentVisionEditable()) {
            $(this.el).find(this.sel.EDIT_TEXT).show();
        }
    },
    onTextMouseLeave: function() {
        if (this.currentVisionEditable()) {
            $(this.el).find(this.sel.EDIT_TEXT).hide();
        }
    },
    onEditClick: function() {
        if (this.currentVisionEditable()) {
            $(this.el).find(this.sel.TEXT_CONTAINER).hide();
            $(this.el).find(this.sel.EDIT_FORM).show();
        }
    },
});

App.Backbone.View.Vision = Backbone.View.extend({
    tagName: "li",
    className: VISION_CLASS,
    sel: {
        SELECTED_CLASS : "VisionSelected",
        USER_NAME : ".VisionUserName",
        PICTURE : ".VisionPicture",
        COMMENT_CONTAINER : ".VisionCommentContainer",
        COMMENT_INPUT : ".AddVisionCommentInput",
        // Overlay
        REPOST : ".Repost",
        MOVE : ".Move",
        //ADD_EXISTING_VISION_SELECTOR : ".AlreadyHaveVision",
        ADD_EXAMPLE_VISION: ".AddVisionNotAuthenticated",
    },
    constant: {
        ANIMATION_TIME : 150,
    },
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
            "mouseenter" : "mouseEnter",
            "mouseleave" : "mouseLeave",
        };
        _events["click " + this.sel.USER_NAME] = "gotoUser";
        _events["click " + this.sel.REPOST] = "repostVision";
        _events["keyup " + this.sel.COMMENT_INPUT] = "visionCommentInput";
        _events["click " + this.sel.PICTURE] = "itemSelect";
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
        if(selected) $(this.el).addClass(this.sel.SELECTED_CLASS);

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
        $(this.el).find(this.sel.COMMENT_CONTAINER).append(this.comments);

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
        $(this.el).find(selector).fadeIn(this.constant.ANIMATION_TIME);
    },

    hideElement: function(selector) {

        //Get element
        var element =  $(this.el).find(selector);

        //Hide
        if(element.is(":visible"))
            element.fadeOut(this.constant.ANIMATION_TIME);
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
                this.showElement(this.sel.ADD_EXAMPLE_VISION);  
            }
        } else if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            // don't show anything
        } else {
            //Repost
            if(!App.Var.Model.inVisionList(this.model)) {
                this.showElement(this.sel.REPOST);
            }
        }
        //TODO: Add the case when they come to another persons page
        // AND they are not logge din
        // Show the instructions bar (box)  

        //On your own board show move butotn!
        if (pageMode == App.Const.PageMode.USER_PROFILE &&
            App.Var.Model.currentUserId() == USER.id) {
            this.showElement(this.sel.MOVE);
        }

        //Vision Overlay

    },
    mouseLeave: function() {
        
        //Get current state
        var pageMode = App.Var.Model.pageMode();

        //Get all of the possible overlays
        var buttons = [this.sel.ADD_EXAMPLE_VISION,
                       this.sel.REPOST,
                       this.sel.MOVE];
        
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
            var text = $.trim($(this.el).find(this.sel.COMMENT_INPUT).val());
            if (text.length > 0) {
                App.Var.View.addVisionComment(this.model.visionId(), text);
            }
        }
    },
});

App.Backbone.View.Page = Backbone.View.extend({
    initialize: function() {
        _.bindAll(this, "masonryReload",
                        // Vision details modal
                        "showVisionDetails",
                        "hideVisionDetails",

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
                        "hideUserInformation");
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
        this.visionDetails = null;
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
        if (DEBUG) console.log("VISION " + visionId + " : " + text);

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
        if (this.visionDetails != null) {
            this.visionDetails.renderComments();
        }
    },
    ajaxAddVisionCommentError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    showVisionDetails: function(visionModel) {
        this.currentVision = visionModel;

        // Note: jQuery text() method escapes html brackets and stuff
        var modal = $(VISION_DETAILS_MODAL).first();


        this.visionDetails = new App.Backbone.View.VisionDetailsModal({model: this.currentVision});
        modal.empty().append(this.visionDetails.el);
        $("body").addClass("NoScroll");
        modal.fadeIn("slow");
    },
    hideVisionDetails: function() {
        var modal = $(VISION_DETAILS_MODAL).first().fadeOut("fast");
        $("body").removeClass("NoScroll");
    },

    /*
     * Changing page mode triggered by set of this.model.pageMode
     */
    changePageMode: function() {
        if (DEBUG) console.log("CHANGE MODE: " + this.model.pageMode());

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
        if (DEBUG) console.log("VISION LIST: " + JSON.stringify(visionIds));

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
                    if (DEBUG) console.log("Success: " + JSON.stringify(data));
                    App.Var.Model.addVision(data.newVision);
                    $("#AddVisionModal").modal("hide");
                },
                // error
                function(jqXHR, textStatus, errorThrown) {
                    console.log("Error");
                }
        );
    });
});
/* $eof */
