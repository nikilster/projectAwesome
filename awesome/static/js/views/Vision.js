
var VISION_CLASS = "Vision";
var VISION_CLASS_SELECTOR = "." + VISION_CLASS;

App.Backbone.View.Vision = Backbone.View.extend({
    tagName: "li",
    className: VISION_CLASS,
    sel: {
        SELECTED_CLASS : "VisionSelected",
        USER_NAME : ".VisionUserName",
        PICTURE : ".VisionPicture",
        MORE_COMMENTS: ".MoreComments",
        COMMENT_CONTAINER : ".VisionCommentContainer",
        COMMENT_INPUT : ".AddVisionCommentInput",
        LIKE: ".VisionLikeInfo",
        // Overlay
        REPOST : ".Repost",
        MOVE : ".Move",
        ONBOARDING_ADD_VISION: ".AddVisionNotAuthenticated",
        ONBOARDING_REMOVE_VISION: ".RemoveVisionNotAuthenticated"
    },
    constant: {
        ANIMATION_TIME : 150,
        // Number of comments shown in vision tile
        NUM_COMMENTS : 4,
    },
    initialize: function() {
        _.bindAll(this, "itemSelect", "renderComment",
                        "mouseEnter", "mouseLeave",
                        "repostVision", "removeVision", "gotoUser",
                        "commentInputKeydown",
                        "onNewComment",
                        "onResize",
                        //Called from Like view
                        "showLikes"
                        );
        assert (typeof this.options.parentView != 'undefined',
                "No parent view");
        if (this.options.parentView) {
            this.parentView = this.options.parentView;
        } else {
            this.parentView;
        }

        this.model.bind("change", this.render, this);
        this.model.bind("new-comment", this.onNewComment, this);
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
        _events["keydown " + this.sel.COMMENT_INPUT] = "commentInputKeydown";
        _events["click " + this.sel.PICTURE] = "itemSelect";
        _events["click " + this.sel.MORE_COMMENTS] = "itemSelect";
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
        var pictureClass = "";
        if (userLoggedIn()) {
            pictureClass = "Zoom";
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

        var moreCommentsVisibility = "Hidden";
        if (userLoggedIn() &&
            (pageMode == App.Const.PageMode.HOME_USER ||
             pageMode == App.Const.PageMode.FEED ||
             pageMode == App.Const.PageMode.USER_PROFILE) &&
            this.hasMoreComments()) {
            moreCommentsVisibility = "";
        }

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
        } else if (pageMode == App.Const.PageMode.USER_PROFILE ||
                   pageMode == App.Const.PageMode.VISION_DETAILS) {
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
                    }
            cursorClass = "MasonryItemPointerCursor";
        }
        if (pageMode == App.Const.PageMode.USER_PROFILE ||
            pageMode == App.Const.PageMode.VISION_DETAILS ||
            pageMode == App.Const.PageMode.FEED) {
            if (userLoggedIn() &&
                (false == this.model.isPublic())) {
                    visionPrivateVisibility = "";
            }
        }

        //Clean for html (using it in the alt=" attribute of the image so don't want '' or "")
        var alt = _.escape(this.model.text());
        var text = linkify(this.model.text());

        //Selected
        if(selected) $(this.el).addClass(this.sel.SELECTED_CLASS);

        //"Any progress?"
        var commentPrompt = this.model.getCommentPrompt(App.Var.Model.loggedInUserId());

        //Cursor
        //TODO: Figure out how to design move

        var variables = {text : text,
                         alt: alt,
                         pictureClass: pictureClass,
                         pictureUrl: pictureUrl,
                         moveDisplay: moveDisplay,
                         removeDisplay: removeDisplay,
                         repostDisplay: repostDisplay,
                         mineDisplay: mineDisplay,
                         removeButtonVisibility: removeButtonVisibility,
                         addCommentVisibility: addCommentVisibility,
                         moreCommentsVisibility: moreCommentsVisibility,
                         visionPrivateVisibility: visionPrivateVisibility,
                         name: this.model.user().fullName(),
                         nameDisplay: nameDisplay,
                         parentUserVisibility: parentUserVisibility,
                         parentUserId: parentUserId,
                         parentUserName: parentUserName,
                         userId: this.model.userId(),
                         profile: USER['picture'],
                         commentPrompt: commentPrompt,
                        };

        var template = _.template($("#VisionTemplate").html(), variables);
        $(this.el).html(template);

        if (this.model.like() != null) {
            var likeView = new App.Backbone.View.Like(
                                                { model: this.model.like(),
                                                  parentView: this });
            $(this.el).find(this.sel.LIKE).append(likeView.el);
        }

        this.comments = []
        var commentList = this.model.comments().last(this.constant.NUM_COMMENTS);
        for (var i = 0 ; i < commentList.length ; i++) {
            this.renderComment(commentList[i], i);
        }
        $(this.el).find(this.sel.COMMENT_CONTAINER).append(this.comments);

        $(this.el).find(this.sel.COMMENT_INPUT).autosize({callback:
                                                          this.onResize})
                                               .placeholder();

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
            if (App.Var.Model.useTestVisionBoard()) {
                this.model.toggleSelected();
                
                //TODO: Why is this enter called?
                this.mouseEnter();
            }
        } else if (pageMode != App.Const.PageMode.EXAMPLE_VISION_BOARD) {
            //App.Var.View.showVisionDetails(this.model);
            App.Var.Model.setCurrentVision(this.model);
            App.Var.Router.navigate("/vision/" + this.model.visionId(),
                                    {trigger: true});
        }

        //Mixpanel
       this.trackVisionAnalytics("Vision Clicked");
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
                if (App.Var.Model.useTestVisionBoard()) {
                    this.showElement(this.sel.ONBOARDING_ADD_VISION);  
                }
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

        //Mixpanel
        mixpanel.track("Add To Example Visions");
        
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

        this.trackVisionAnalytics("Repost");
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

        var targetUserId = this.model.userId();

        //Mixpanel
        this.trackVisionAnalytics("Go to User", {'User Being Viewed': targetUserId});

        App.Var.Router.navigate("/user/" + targetUserId, {trigger: true});
    },
    
    showLikes: function() {
        App.Var.View.showVisionLikes(this.model.visionId());
    },

    commentInputKeydown: function(e) {
        var code = (e.keyCode ? e.keyCode : e.which);
        if (code == 13) {
            e.preventDefault(); 
            var text = $.trim($(this.el).find(this.sel.COMMENT_INPUT).val());
            if (text.length > 0) {
                this.model.addVisionComment(text);
            }
        }
    },
    onResize: function() {
        if (this.parentView != null) {
            this.parentView.onVisionResize();
        }
    },
    onNewComment: function() {
        if (this.parentView != null) {

            // resizing the textarea to default size also
            $(this.el).find(this.sel.COMMENT_INPUT).removeAttr("style");

            this.parentView.onNewComment();
        }
    },

    // Has more comments than MAX_COMMENTS shown in vision tile
    hasMoreComments: function() {
        return this.model.comments().length > this.constant.NUM_COMMENTS;
    },

    //Mixpanel
    trackVisionAnalytics: function(actionName, properties) {

        var loggedIn = userLoggedIn ? "True" : "False";
        var page = App.Var.Model.pageString();
        var visionId = this.model.visionId();

        //Optional Argument
        if(typeof properties === 'undefined')
            properties = {};

        var baseProperties = {
            'Logged In': loggedIn,
            'Page': page,
            'Vision Id': visionId
        };

        //Merge Properties
        var allProperties = $.extend(baseProperties, properties);

        //Track
        mixpanel.track(actionName, allProperties);
    }
});
