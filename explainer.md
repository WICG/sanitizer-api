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
  context element, like assigning to `innerHTML` would; applies a filter,
  while enforcing an XSS-focused baseline; and finally replaces the children
  of `this` with the results.
- `Element.setHTMLUnsafe(string, {options})` - Like above, but it does not
  enforce a baseline. E.g. if the filter is configured to allow a `<script>`
  element, then a `<script>` would be inserted. If no filter is configured
  then no filtering takes place.
- `Document.parseHTML(string, {options})` (static method) - Creates a new
  Document instance, and parses `string` as its content, like
  `DOMParser.parseFromString` would. Applies a filter, while enforcing an
  XSS-focused baseline. Returns the document.
- `Document.parseHTMLUnsafe(string, {options})` (static method) - Like
  above, but it will not enforce a baseline or apply any filter by default.

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
  other than the baseline?
- Defaults: All of these are new methods without legacy usage. Would DSD
  parsing default to `true`? (Probably. Decision lies with WHATWG.)
- Should the filter config be a separate object, or should it be a plain dictionary?
  - Reasons pro dictionary:
     - Simpler.
  - Reasons pro object:
     - Allows to pre-process the config and to amortize the cost over many calls.
     - Allows adding other useful config operations, like introspection.
- Exact filter options syntax. I'm assuming this will follow the discussion in
  #181.
- Naming is TBD. Here I'm trying to follow the preferences expressed in the
  recent 'sync' meeting.

## Examples
```js
// TODO
```
