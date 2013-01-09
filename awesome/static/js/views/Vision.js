
var VISION_CLASS = "Vision";
var VISION_CLASS_SELECTOR = "." + VISION_CLASS;

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
        ONBOARDING_ADD_VISION: ".AddVisionNotAuthenticated",
        ONBOARDING_REMOVE_VISION: ".RemoveVisionNotAuthenticated"
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
        _events["click " + this.sel.ONBOARDING_ADD_VISION] = "onboardingAddVision";
        _events["click " + this.sel.ONBOARDING_REMOVE_VISION] = "onboardingRemoveVision";
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

        var visionPrivateVisibility = "Hidden";

        var parentUserVisibility = "Hidden";
        var parentUserId = "";
        var parentUserName = "";
        if (this.model.hasParent()) {
            var parentUserVisibility = "";
            parentUserId = this.model.parentUser().userId();
            parentUserName = this.model.parentUser().fullName();
        }

        if (pageMode == App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            removeDisplay = "inline-block";

        } else if (pageMode == App.Const.PageMode.HOME_GUEST) {
            nameDisplay = "block";
        } else if (pageMode == App.Const.PageMode.HOME_USER) {
            nameDisplay = "block";
            if (App.Var.Model.inVisionList(this.model)) {
                mineDisplay = "inline-block";
                selected = true;
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
                    } else {
                        repostDisplay = "inline-block";
                    }
                }
                if (!this.model.isPublic()) {
                    visionPrivateVisibility = "";
                }
            }
            cursorClass = "MasonryItemPointerCursor";
        }

        //Clean for html (using it in the alt=" attribute of the image so don't want '' or "")
        var alt = _.escape(this.model.text());
        var text = linkify(this.model.text());

        //Selected
        if(selected) $(this.el).addClass(this.sel.SELECTED_CLASS);

        //Cursor
        //TODO: Figure out how to design move

        var variables = {text : text,
                         alt: alt,
                         pictureUrl: pictureUrl,
                         moveDisplay: moveDisplay,
                         removeDisplay: removeDisplay,
                         repostDisplay: repostDisplay,
                         mineDisplay: mineDisplay,
                         removeButtonVisibility: removeButtonVisibility,
                         addCommentVisibility: addCommentVisibility,
                         visionPrivateVisibility: visionPrivateVisibility,
                         name: this.model.name(),
                         nameDisplay: nameDisplay,
                         parentUserVisibility: parentUserVisibility,
                         parentUserId: parentUserId,
                         parentUserName: parentUserName,
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


        //Make the "Add To MY Vision Board" Button clickable
        //TODO: Need to figure out the correct place / best way for ->
        $()
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
            
            //TODO: Why is this enter called?
            this.mouseEnter();
        } else if (pageMode != App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            //App.Var.View.showVisionDetails(this.model);
            App.Var.Model.setCurrentVision(this.model);
            App.Var.Router.navigate("/vision/" + this.model.visionId(),
                                    {trigger: true});
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
                this.showElement(this.sel.ONBOARDING_ADD_VISION);  
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

        //On your own board show move button!
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
        var buttons = [this.sel.ONBOARDING_ADD_VISION,
                       this.sel.REPOST,
                       this.sel.MOVE];
        
        //If a overlay / button is showing, hide it
        for (var i = 0 ; i < buttons.length ; i++) {
            this.hideElement(buttons[i]);
        }

    },

    //Add to the onboarding first vision board
    onboardingAddVision: function(e) {
        e.preventDefault();
        this.model.select();
    },

    //Remove from the onboarding initial vision board
    onboardingRemoveVision: function(e) {
        e.preventDefault();
        this.model.unselect();
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
