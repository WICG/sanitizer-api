 Sanitizer API - FAQs
======================

## How do I use the Sanitizer API

Construct a new Sanitizer, using either the defaults or suppliying a custom
configuration, and then pass in a string, a fragment, or an entire document
for sanitization.

```js
const s = new Sanitizer();

// Returns a DOM Fragment equivalent to "<em>Hello World</em>".
s.sanitize("<em>Hello World</em><script>alert('surprise');</script>");
```

## Can I use the Sanitizer in my app?

Not yet. Current browser support is preliminary and incomplete and still
diverges in several details. And the specification itself is still in flux.
We expect to be working through these issues in the coming months.

If you wish to try it out already:

* Firefox: Go to `about:config`, search for the `dom.security.sanitizer.enabled`
  flag and set it to true

* Chromium / Chrome: Start the browser with the
  `--enable-blink-features=SanitizerAPI` flag.

## Do I have to supply my own Sanitizer configuration? What is the default?

The default configuration will block all content that causes script execution.
unknown elements, plus a handful of deprecated elements.
It is safe against any direct XSS.

```js
const default_sanitizer = new Sanitizer();

// Returns a DOM Fragment equivalent to "<em>Hello World</em>".
default_sanitizer.sanitize("<em>Hello World</em>");

// Complex formatting is allowed by default. This will return a fragment
// equivalent to its input.
default_sanitizer.sanitize("<div id='hello'><span style='font-weight: bold'>Hello World</span></div>");

// Script execution is no-no: Returns "<p>Hello</p>"
default_sanitizer.sanitize("<p onclick='alert(\'surprise\')'>Hello</p>");
```

## Is Sanitizer output secure?

'Secure' means different things in different contexts. The Sanitizer guarantees
safety from direct script execution in all configurations. This cannot be
overridden by custom configurations.

```js
// Produces an empty fragment. There is no way to allow the <script> element.
new Sanitizer({"allowElements": ["script"]}).sanitize("<script>alert('surprise')</script>");
```

Other notions of safety can likely be configured. For example, if an
application relies on the `id=` attribute and does not wish user-supplied input
to introduce unforseen `id=` attribute values, then the application can easily
configure a block a Sanitizer to block the this attribute. However, the
application must ensure on its own that all parts of the application
(including any of its dependencies) will adhere to this restriction.

Note: When we refer to "direct" script execution, we mean all markup that will
  cause the browser to parse and execute script, such as the `<script>` element
  or the `onclick=` event handler attribute. The adjective "direct" is meant
  to distinguish this from indirect script execution via
  [script gadgets](https://dl.acm.org/doi/abs/10.1145/3133956.3134091). Script
  gadgets are application dependent and cannot be sanitized in a generic API.
  But you can likely use custom Sanitizer configurations adapted to your
  application's needs.


## When should I use `.sanitize` vs `.sanitizeToString`?

`.sanitize` and `.sanitizeToString` do the same work, except `.sanitizeToString`
will serialize the result fragment into a string and return that. This has
several consequences:

* There are XSS risk with parsing and re-parsing HTML strings, known
  collectively as
  [mXSS](https://hackinparis.com/data/slides/2013/slidesmarioheiderich.pdf).
  Examples would be when the DOM node a string gets inserted into has special
  parsing rules, such as SVG nodes or the `<plaintext>` element.
  These pitfalls are avoided entirely when using `.sanitize`.

* Since in all likelihood the Sanitizer result will eventually
  be inserted into the DOM, retaining the fragment (i.e. `.sanitize`)
  rather than a serialization that needs to be re-parsed
  (i.e. `.sanitizeToString`) is more efficient, since you avoid un-parsing
  and then re-parsing the same data that has already been parsed for us.

The Sanitizer API spec editors recommend to prefer `.sanitize`, and to use
`.sanitizeToString` in cases where existing code structure or
other constraints make it difficult to use a type other than string.

## Can I use the Sanitizer API together with Trusted Types?

Yes, please. We see these as APIs that solve different aspects of the
same problem. They are separate, but should work well together.

Details of Santizer API/Trusted Types integration are still being worked out.


## Can I sanitize myself rich?

Of course. Firefox's [Client Bug Bounty Program includes the Sanitizer API
under certain conditions](https://www.mozilla.org/en-US/security/client-bug-bounty/#exploit-mitigation-bounty).

