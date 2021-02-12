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

* Firefox: Enable the `sanitizer.enabled` preference.
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

// Complex formatting is allowed by default. This will pass unchanged.
default_sanitizer.sanitize("<div id='hello'><span style='font-weight: bold'><Hello World</span></div>");

// Script execution is no-no: Returns "<p>Hello</p>"
default_sanitizer.sanitize("<p onclick='alert(\'surprise\')'>Hello</p>");
```

## Is Sanitizer output secure?

'Secure' means different things in different contexts. The Sanitizer guarantees
safety from direct script execution in all configurations. This cannot be
overridden by custom configurations.

```js
// Produces an empty fragment. There is no way to allow the <script> element.
new Sanitizer({"allowElements": ["script"]}.sanitize("<script>alert('surprise')</script>");
```

Other notions of safety can likely be configured. For example, if an
application relies on the `id=` attribute and does not wish user-supplied input
to introduce unforseen `id=` attribute values, then the application can easily
configure a block a Sanitizer to block the this attribute. However, the
application must ensure on its own that all parts of the application
(including any of its dependencies) will adhere to this restriction.


## When should I use `.sanitize`, when `.sanitizeToString`?

This is up to you. `.sanitize` and `.sanitizeToString` do the same work,
except `.sanitizeToString` will serialize the result fragment into a string
and return that. Since in all likelihood the Sanitizer result will eventually
be inserted into the DOM, retaining the fragment (i.e. `.sanitize`) rather
than a serialization that needs to be re-parsed (i.e. `.sanitizeToString`)
is more efficient.

Additionally, handling a string opens up the possibility of mXSS if the
DOM node it gets inserted into has special parsing rules, such as SVG nodes
or the `<plaintext>` element.

The recommendation of the Sanitizer API spec editors is to prefer `.sanitize`,
and to use `.sanitizeToString` in cases where existing code structure or
other constraints make it difficult to use a type different from string.

TODO: Link to mXSS explanation.


## Can I use the Sanitizer API together with Trusted Types?

Yes, please. We see these as APIs that solve different aspects of the
same problem. THey are separate, but should work well together.

Details of Santizer API/Trusted Types integration are still being worked out.


## Can I sanitize myself rich?

Of course. Firefox's Client Bug Bounty Program includes the Sanitizer API
under certain conditions. See: https://twitter.com/freddyb/status/1304331985398235138

