[![Build Status](https://travis-ci.org/WICG/sanitizer-api.svg?branch=main)](https://travis-ci.org/WICG/sanitizer-api)

# Sanitization Explainer

## The Problem

Various web applications often need to work with strings of HTML on the client-side. This might take place, for instance, as part of a client-side templating solution or perhaps come to play through the process of rendering user-generated content. The key problem is that it remains difficult to perform these tasks in a safe way. This is specifically the case because the naive approach of joining strings together and stuffing them into an [Element](https://dom.spec.whatwg.org/#element)'s [`innerHTML`](https://w3c.github.io/DOM-Parsing/#widl-Element-innerHTML) is fraught with risks. A very common negative implication concerns the JavaScript execution, which can occur in a number of unexpected ways.

To address the problem, libraries like [DOMPurify](https://github.com/cure53/DOMPurify) attempt to carefully manage the inputs and alleviate risks. This is usually accomplished through parsing and sanitizing strings before insertion and takes advantage of an allowlist for constructing a DOM and handling its components. This is considerably safer than doing the same on the server-side, yet much untapped potential can still be observed when it comes the client-side sanitization.

As it stands, every browser has a fairly good idea of when and how it is going to execute code. Capitalizing on this, it is possible to improve the user-space libraries by teaching the browser how to render HTML from an arbitrary string in a safe manner. In other words, we seek to make sure that this happens in a way that is much more likely to be maintained and updated along with the browsers’ ever-changing parser implementations.


## Goals

Provide a **browser-maintained** "ever-green", **safe**, and **easy-to-use**
library for **user input sanitization** as part of the general **web platform**.

* **user input sanitization**: The basic functionality is to take a string,
  and turn it into strings that are safe to use and will not cause inadvertent
  execution of JavaScript.

* **browser-maintained**, "**ever-green**" / as part of the general
  **web platform**: The library is shipped with the browser, and will be
  updated alongside it as bugs or new attack vectors are found.

* **Safe** and **easy-to-use**: The API surface should be small, and the
  defaults should make sense across a wide range of use cases.

### Secondary Goals

* Cover **existing browser functionality**, especially the [sanitization of
  clipboard](https://www.w3.org/TR/clipboard-apis/#pasting-html) data.

* **Easy things should be easy.** This requires easy-to-use and safe defaults,
  and a small API surface for the common case.

* Cover a **reasonably wide range of base requirements**, but be open to more
  advanced use cases or future enhancements. This probably requires some sort
  of configuration or options, ideally in a way that both the developer and a
  security reviewer should be able to reason about them.

* Should be **integratable into other security mechanisms**, both browser
  built-ins and others.

* Be **poly-fillable**, although the polyfill would presumably have different
  security and performance properties.

### Non-goals

Force the use of this library, or any other enforcement mechanism. Some
applications will have sanitization requirements that are not easily met by
a general purpose library. These should continue to be able to use whichever
library or mechanism they prefer. However, the library should play well with
other enforcement mechanisms.

## Proposed API

*Context: Various disagreements over API details lead to a re-design of the
Sanitizer API. This presents a new API proposal (April '23, based on #192):*

There is a 2x2 set of methods that parse and filter the resulting node tree:
On one axis they differ in the parsing context and are analogous to `innerHTML`
and `DOMParser`'s `parseFromString()`; on the other axis, they differ
in whether they enforce an XSS-focused security baseline or not. These two
aspects pair well and yield:

- `Element.setHTML(string, {options})` - Parses `string` using `this` as
  context element, similar in spirit to `innerHTML`; applies a filter,
  while enforcing an XSS-focused baseline; and finally replaces the children
  of `this` with the results.
- `Element.setHTMLUnsafe(string, {options})` - Like above, but it does not
  enforce a baseline. E.g. if the filter is configured to allow a `<script>`
  element, then a `<script>` would be inserted. If no filter is configured
  then no filtering takes place.
- `Document.parseHTML(string, {options})` (static method) - Creates a new
  Document instance, and parses `string` as its content similar to how
  `DOMParser.parseFromString` would. Applies a filter, while enforcing an
  XSS-focused baseline. Returns the document.
- `Document.parseHTMLUnsafe(string, {options})` (static method) - Like
  above, but it will not enforce a baseline or apply any filter by default.

Note that while these methods are similar to `innerHTML` and `DOMParser`'s
`parseFromString`, we expect some differences in addition to HTML filtering:
For example, these new methods should support declarative shadow DOM by default.
They will not support creation of XML documents.

All variants take an options dictionary with a `filter` (naming TBD) key and a
filter configuration. The options dictionary can be easily extended to accept
whatever parsing parameters make sense.

The 'safe' methods may have some built-in anti-XSS behaviours that are not
expressibleby the config, e.g. dropping `javascript:`-URLs in contexts
that navigate.

The 'unsafe' methods will not apply any filtering if no explicit config is
supplied.

## Major differences to previously proposed APIs:

The currently proposed API differs in a number of aspects:

- Two sets of methods, `innerHTML`-like and `DOMParser`-like.
- Since the 'sanitizer' config can now be used in both safe and unsafe ways,
  it's arguably no longer a sanitizer config but a filter config.
- Enforcement of a security baseline depends on the method. The filter/sanitizer
  config can now be used differently, either in a guaranteed-secure way or in
  use-config-as-written way.

## Open questions:

- Defaults: If no filter is supplied, do the safe methods have any filtering
  other than the baseline? (For further discussion, see #188.)
- Should the filter config be a separate object, or should it be a plain
  dictionary? (As-is, it should probably be a dictionary. An object would
  require either compelling performance numbers, or a compelling operation that
  would only work with a pre-processed dictionary.)
- Exact filter options syntax. I'm assuming this will follow the discussion in
  #181.
- Naming is TBD. Here I'm trying to follow the preferences expressed in the
  recent 'sync' meeting.

## Examples

The new APIs, in their most basic form:
```js
const example = `<b onclick="alert(1)">hello world</b>`;
const element = document.createElement("div");

// Modify element:
element.setHTML(example);  // <div><b>hello world</b></div>
element.setHTMLUnsafe(example);  // <div><b onclick="alert(1)">hello world</b></div>

// Return a Document instance:
Document.parseHTML(example);  // <html><head></head><body><b>hello world</b></body></html>
Document.parseHTMLUnsafe(example);  // <html><head></head><body><b onclick="alert(1)">hello world</b></body></html>
```

Parsing observes its contexts:
```js
const example_tr = `<tr><td>A table row.</td></tr>`;
const table = document.createElement("table");

element.setHTML(example_tr);  // <div>A table row.</div>
table.setHTML(example_tr);  // <table><tbody><tr><td>A table row.</td></tr></tbody></table>
Document.parseHTML(example_tr);  // <html><head></head><body>A table row.</body></html>
```
All of these would have had identical results if the "unsafe" variants had
been used.

Parsing follows HTML parsing rules, unlike `innerHTML`, where it depends on the
document type:
```js
const element_xml = new DOMParser().parseFromString("<html xmlns='http://www.w3.org/1999/xhtml'><body><div/></body></html>", "application/xhtml+xml").getElementsByTagName("div")[0];
const example_not_xml = "<bLoCkQuOtE>bla";

element_xml.getRootNode().contentType;  // application/xhtml+xml
element_xml.innerHTML = example_not_xml;  // Throws.
element_xml.setHTML(example_not_xml);  // <div xmlns="http://www.w3.org/1999/xhtml"><blockquote>bla</blockquote></div>
                                       // Note case and closing elements.
element.setHTML(example_not_xml);  // Same as above.
```

The "safe" methods remove all script-y content defined by the platform and
let the rest pass:
```js
element.setHTML(`<a href=about:blank onclick=alert(1) onload=alert(2) id=myid class=something><script>alert(3);</script>`);
// <div><a href="about:blank" id="myid" class="something"></a></div>
```

The operation of the built-in sanitizer can be configured to suit your
applications' needs. Both "safe" and "unsafe" versions can take a configuration.
(Please note that naming and structure here is rather preliminary,
but we expect these capabilities to be in the final standard.)

The "safe" version will ignore configuration items that break its security
guarantees:
```js
const an_unsafe_config = { 'allowElements': [ { name: 'script' } ] };
element.setHTML("<script>", { sanitizer: an_unsafe_config });  // <div></div>
element.setHTMLUnsafe("<script>", { sanitizer: an_unsafe_config });  // You now have a script. Congrats.
```

For elements, the HTML namespace is default. For attributes, the null namespace.
Other namespaces can be supported. A string entry stands for a dictionary with
only the name, in the HTML/null namespace (for elements/attributes,
respectively).
``` js
const config_with_namespaces = {
  allowElements: [
    'a',  // The HTML anchor element.
    { name: 'a' },  // Also the HTML anchor element.
    { name: 'a', namespace: 'http://www.w3.org/1999/xhtml' },  // Another one.
    { name: 'a', namespace: 'http://www.w3.org/2000/svg' }  // SVG's anchor element
  ],
  allowAttributes: [
    'href',  // An href attribute. The one you'd expect on an HTML anchor.
    { name: 'href' },  // The very same.
    { name: 'href', namespace: '' },  // There it is again.
    { name: 'href', namespace: 'http://www.w3.org/1999/xlink' },  // xlink:href. SVG sometimes uses this.
    { name: 'href', namespace: 'http://www.w3.org/1999/xhtml' }  // This isn't a thing.
        // It won't match any HTML-defined href attributes. Probably the config
        // author made an error.
  ]
};
```

There are two ways you can build up a config: Specify the elements & attributes
you wish to allow. This is easy to read and makes it easy to understand what
to expect in the sanitizer output. Or you can specify what elements & attributes
you wish to block. This effectively specifies the sanitizer output relative to
the built-in list. This can be useful if you wish to mostly retain the built-in
defaults.

```js
const config_allow = {
  allowElements: [ "div", "p", "em", "b" ]  // Allows only those four elements.
      // Output with "safe" and "unsafe" methods should be the same.
};
const config_block = {
  blockElements: [ "style" ]  // Allows a lot of things. But not <style>.
      // And not XSS-y stuff, either, if used with a "safe" method.
      // Output with "safe" and "unsafe" methods might be quite different.
};
```
