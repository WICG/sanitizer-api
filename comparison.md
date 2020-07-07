# A Feature Comparison of Existing Sanitzer APIs

This document lists the features of similarly spirited sanitizers.

## [DOMPurify][dompurify]

General API notes:

* DOMPurify has a built-in, modifiable default config. The sanitize call
  also accepts an options dictionary on every call. This proposal instead
  allows creation of sanitizer objects from an options dictionary, and offers
  several read-only sanitizers for easy-to-use defaults.

* DOMPurify uses options and a single method with different return types
  depending on the options set. Here, we instead have different methods for
  different return types.

* DOMPurify has a lot more options then the current Sanitzer API proposal.

* There is presently no equivalent to [hooks][dompurify-hooks].

[dompurify-hooks]: https://github.com/cure53/DOMPurify#hooks

List of DOMPurify options: (options collected [here][dompurify-options-1] and
[here][dompurify-options-2])

[dompurify]: https://github.com/cure53/DOMPurify
[dompurify-options-1]: https://github.com/cure53/DOMPurify#can-i-configure-dompurify
[dompurify-options-2]: https://github.com/cure53/DOMPurify/blob/master/src/purify.js

* Specify return value type: (Might also influence allowed tags):
   * `RETURN_DOM  // returns HTMLBodyElement`
   * `RETURN_DOM_FRAGMENT  // returns  DocumentFragment`
   * `RETURN_DOM_IMPORT  // modifier to RETURN_DOM_FRAGMENT`
   * `RETURN_TRUSTED_TYPE  // return TrustedHTML`
* Limit/extend which content is allowed:
   * `ALLOWED_TAGS`
   * `ALLOWED_ATTR`
   * `FORBID_TAGS`
   * `FORBID_ATTR`
   * `ADD_TAGS`
   * `ADD_ATTR`
   * `ALLOW_DATA_ATTR`
   * `ALLOW_UNKNOWN_PROTOCOLS`
   * `ALLOWED_URI_REGEXP`
   * `ADD_URI_SAFE_ATTR`
   * `ALLOW_ARIA_ATTR`
   * `SAFE_FOR_TEMPLATES  // strip common template markers (like <%..%>)`
   * `SAFE_FOR_JQUERY`
* Profile options, that enable several options at once:
   * `USE_PROFILES  // predefined sets of ALLOWED_TAGS`
* Miscellaneous::
   * `WHOLE_DOCUMENT`
   * `SANITIZE_DOM`
   * `FORCE_BODY`
   * `KEEP_CONTENT`
   * `IN_PLACE`

DOMPurify hooks: (without equivalent in the current proposal)
* `beforeSanitizeElements`
* `uponSanitizeElement  // No 's' - called for every element`
* `afterSanitizeElements`
* `beforeSanitizeAttributes`
* `uponSanitizeAttribute`
* `afterSanitizeAttributes`
* `beforeSanitizeShadowDOM`
* `uponSanitizeShadowNode`
* `afterSanitizeShadowDOM`

## TODO

* Clipboard Sanitizers in Browsers
* [Bleach](https://github.com/mozilla/bleach)

