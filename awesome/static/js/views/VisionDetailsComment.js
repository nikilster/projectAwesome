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

