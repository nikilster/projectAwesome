App.Backbone.Model.Vision = Backbone.Model.extend({
    defaults: {
        id: -1,
        parentId: -1,
        rootId: -1,
        userId: -1,
        text: "",
        privacy: -1,
        created: null,
        createdDate: null,
        picture: null,
        comments: new App.Backbone.Model.VisionCommentList(),
        isSelected: false,
        parentUser: null,
        user: null,
        like: null,
    },
    initialize: function(attributes, options) {
        _.bindAll(this, "ajaxLikeSuccess", "ajaxLikeError",
                        "ajaxCommentSuccess", "ajaxCommentError");
        this.set({
            picture: new App.Backbone.Model.Picture(this.get("picture")),
            comments: new App.Backbone.Model.VisionCommentList(this.get("comments")),
            parentUser: new App.Backbone.Model.User(this.get("parentUser")),
            user: new App.Backbone.Model.User(this.get("user")),
        });

        if (this.get("like") != null) {
            this.set({ like: new App.Backbone.Model.Like(this.get("like")) });
        }

        if (this.created() != null) {
            this.set({ createdDate: dateFromUTC(this.get("created"))});
        }

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
    isSelected: function() { return this.get("isSelected"); },
    comments: function() { return this.get("comments"); },
    created: function() { return this.get("created"); },
    createdDate: function() { return this.get("createdDate"); },
    timeString: function() {
        return timeFromToday(this.createdDate());
    },

    hasParent: function() {
        return this.parentId() != 0 && this.parentId() != -1;
    },
    parentUser: function() {
        assert (this.hasParent(), "Should have parent user");
        return this.get("parentUser");
    },
    user: function() {
        return this.get("user");
    },

    isPublic: function() {
        var privacy = this.get("privacy");
        assert(privacy == App.Const.VisionPrivacy.PRIVATE ||
               privacy == App.Const.VisionPrivacy.PUBLIC, "Invalid privacy");
        return privacy == App.Const.VisionPrivacy.PUBLIC;
    },
    like: function() {
        return this.get("like");
    },

    /*  Test to see if this vision was created by the user who is viewing */
    usersOwnVision: function(viewingUsersId) {

        //Logged in user =? vision creator?
        return viewingUsersId == this.userId();
    },

     /* 
        Prompt the user to type
    */
    getCommentPrompt: function(viewingUsersId) {
        
        if(!this.usersOwnVision(viewingUsersId))
            return App.Const.Strings.COMMENT_PROMPT_FRIEND;
        else 
            return App.Const.Strings.COMMENT_PROMPT_OWN;
    },


    //Switch the selection
    toggleSelected: function() {
        if (!this.isSelected()) {
            this.select();
        } else {
            this.unselect();
        }
    },

    setComments: function(comments) {
        this.comments().reset(comments);
    },


    //Select Vision
    select: function() {
    
        //Ignore if this is already selected
        if(this.isSelected()) {
            return;
        }

        //TODO: Why do we have this limit?
        if (App.Var.Model.numSelectedVisions() <
            App.Const.MAX_SELECTED_VISIONS) {
            //Add
            App.Var.Model.addToSelectedVisions(this);

            //Set
            this.set({isSelected: true});
        }
    },

    //Unselect Vision
    unselect: function() {
        //If Already unselected - return
        if(!this.isSelected()) {
            return;
        }

        //Remove
        App.Var.Model.removeFromSelectedVisions(this);

        //Set
        this.set({isSelected: false});

    },

    edit: function(text, isPublic) {
        var privacy = App.Const.VisionPrivacy.PRIVATE;
        if (isPublic) {
            privacy = App.Const.VisionPrivacy.PUBLIC;
        }
        this.set({ 'text' : text,
                   'privacy' : privacy,
                 }, { trigger: false});
        // TODO: Find better way to do this later. Don't have way of
        //       signalling top level view right now from individual vision
        this.trigger("change");
        App.Var.View.masonryReload();
    },
    setLike: function(like, likeCount) {
        // USER MUST BE LOGGED IN
        if (userLoggedIn()) {
            this.like().set({userLike: like, likeCount: likeCount});
        }
    },
    toggleLike: function() {
        if (userLoggedIn() && this.like() != null) {
            if (this.like().userLike() == false) {
                this.ajaxLike(true);
            } else {
                this.ajaxLike(false);
            }
        }
    },
    ajaxLike: function(like) {
        if (DEBUG) console.log("LIKE: " + this.visionId());
        doAjax("/api/user/" + USER['id'] + "/like_vision",
                JSON.stringify({
                                'visionId' : this.visionId(),
                                'like' : like,
                                }),
                this.ajaxLikeSuccess,
                this.ajaxLikeError
        );
    },
    ajaxLikeSuccess: function(data, textStatus, jqXHR) {
        this.setLike(data.like, data.likeCount);
    },
    ajaxLikeError: function(jqXHR, textStatus, errorThrown) {
    },

    addVisionComment: function(text) {
        if (text.length > 0) {
            if (DEBUG) console.log("VISION COMMENT : " + text);

            doAjax("/api/vision/" + this.visionId() + "/add_comment",
                    JSON.stringify({
                                    'visionId' : this.visionId(),
                                    'text' : text,
                                    }),
                    this.ajaxCommentSuccess,
                    this.ajaxCommentError
            );
        }
    },
    ajaxCommentSuccess: function(data, textStatus, jqXHR) {
        var newModel = new App.Backbone.Model.VisionComment(data.newComment);
        this.comments().push(newModel);
        this.trigger("new-comment");

        // TODO: this is kind of a hack for now, but it only renders if the
        //       details modal is displayed so it works.  Later we really want
        //       a way where the add event from the comment list triggers a
        //       re-render
        //if (this.visionDetails != null) {
        //    this.visionDetails.renderComments();
        //}
    },
    ajaxCommentError: function(jqXHR, textStatus, errorThrown) {
        // Do nothing, we already showed an error and don't need to change UI
    },

    deepClone: function() {
        var cloneModel = this.clone();
        cloneModel.set({ picture: this.picture().clone() });
        return cloneModel;
    },
});

