const get = elem => document.getElementById(elem),
					 registerButton = get('register'),
					 loginButton = get('login'),
					 container = get('container')
 
registerButton.onclick = () => {
					 container.className = "active"
}

loginButton.onclick = () => {
						container.className = "close"
}
 
var Alert = {};

(function(Alert) {
  var _container;

  function alert(type, message, title, icon, options) {
    if (typeof options === "undefined") {
      options = {};
    }
    options = $.extend({}, Alert.defaults, options);

    if (!_container) {
      _container = $("#alerts");
      if (_container.length === 0) {
        _container = $("<ul>").attr("id", "alerts").appendTo($("body"));
      }
    }

    if (options.width) {
      _container.css({
        width: options.width
      });
    }

    var alertElem = $("<li>").addClass("alert").addClass("alert-" + type);
    setTimeout(function() {
      alertElem.addClass('open');
    }, 1);

    if (icon) {
      var iconElem = $("<i>").addClass(icon);
      alertElem.append(iconElem);
    }

    var innerElem = $("<div>").addClass("alert-block");
    alertElem.append(innerElem);

    if (title) {
      var titleElem = $("<div>").addClass("alert-title").append(title);
      innerElem.append(titleElem);
    }

    if (message) {
      var messageElem = $("<div>").addClass("alert-message").append(message);
      innerElem.append(messageElem);
    }

    if (options.displayDuration > 0) {
      setTimeout(function() {
        leave();
      }, options.displayDuration);
    } else {
      innerElem.append("<em>Click to Dismiss</em>");
    }

    alertElem.on("click", function() {
      leave();
    });

    function leave() {
      alertElem.removeClass('open');
      alertElem.one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function() {
        alertElem.remove();
      });
    }

    _container.prepend(alertElem);
  }

  Alert.defaults = {
    width: "",
    icon: "",
    displayDuration: 3000,
    pos: ""
  };

  Alert.info = function(message, title, options) {
    return alert("info", message, title, "fa fa-info-circle", options);
  };

  Alert.warning = function(message, title, options) {
    return alert("warning", message, title, "fa fa-warning", options);
  };

  Alert.error = function(message, title, options) {
    return alert("error", message, title, "fa fa-exclamation-circle", options);
  };

  Alert.trash = function(message, title, options) {
    return alert("trash", message, title, "fa fa-trash-o", options);
  };

  Alert.success = function(message, title, options) {
    return alert("success", message, title, "fa fa-check-circle", options);
  };

})(Alert || (Alert = {}));

this.Alert = Alert;

$('#test').on('click', function() {
  Alert.info('Message');
});