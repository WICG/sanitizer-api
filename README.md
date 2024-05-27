# Sanitizer API

The *Sanitizer API* is a proposed new browser API to bring a safe and
easy-to-use capability to sanitize HTML into the web platform.

Status:

* The Sanitizer API is currently being incubated in the
  [Sanitizer API](https://github.com/WICG/sanitizer-api) [WICG](https://wicg.io/),
  with the goal of bringing this to the [WHATWG](https://whatwg.org/).
* The API is not finalized and still subject to change.

Here you can find additional information:

* Implementation Status:
  * [Mozilla position](https://github.com/mozilla/standards-positions/issues/106),
    [WebKit position](https://github.com/WebKit/standards-positions/issues/86),
    [Chrome Status](https://www.chromestatus.com/feature/5786893650231296).
  * [Can I use 'Sanitizer API'](https://caniuse.com/mdn-api_sanitizer)?
  * [Web Platform Tests]( https://wpt.fyi/results/sanitizer-api?label=experimental&label=master&aligned)
    ([test source](https://github.com/web-platform-tests/wpt/tree/master/sanitizer-api)).
* An early [W3C TAG review](https://github.com/w3ctag/design-reviews/issues/619).

## Explainer

The API is still being discussed. Please see the [explainer](explainer.md) for
our current thinking.

## Taking a Step Back: The Problem We're Solving

Various web applications often need to work with strings of HTML on the client-side. This might take place, for instance, as part of a client-side templating solution or perhaps come to play through the process of rendering user-generated content. The key problem is that it remains difficult to perform these tasks in a safe way. This is specifically the case because the naive approach of joining strings together and stuffing them into an [Element](https://dom.spec.whatwg.org/#element)'s [`innerHTML`](https://w3c.github.io/DOM-Parsing/#widl-Element-innerHTML) is fraught with risks. A very common negative implication concerns the JavaScript execution, which can occur in a number of unexpected ways.

To address the problem, libraries like [DOMPurify](https://github.com/cure53/DOMPurify) attempt to carefully manage the inputs and alleviate risks. This is usually accomplished through parsing and sanitizing strings before insertion and takes advantage of an allowlist for constructing a DOM and handling its components. This is considerably safer than doing the same on the server-side, yet much untapped potential can still be observed when it comes the client-side sanitization.

As it stands, every browser has a fairly good idea of when and how it is going to execute code. Capitalizing on this, it is possible to improve the user-space libraries by teaching the browser how to render HTML from an arbitrary string in a safe manner. In other words, we seek to make sure that this happens in a way that is much more likely to be maintained and updated along with the browsers’ ever-changing parser implementations.

### Goals For The Sanitizer API

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

