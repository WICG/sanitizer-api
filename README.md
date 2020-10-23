[![Build Status](https://travis-ci.org/WICG/sanitizer-api.svg?branch=master)](https://travis-ci.org/WICG/sanitizer-api)

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



## Proposal

Note: The proposal is being developed [here](https://wicg.github.io/sanitizer-api/).


We want to develop an API that learns from the
[DOMPurify](https://github.com/cure53/DOMPurify) library. In particular:

* The core API would be a single method which sanitizes a String and returns
  a DocumentFragment.

  * `sanitize(DOMString value)` => `DocumentFragment`

  * Other input types  (e.g. Document or DocumentFragment) can also be
    supported.

  * Other result types (e.g. String-to-String) can also be supported with
    different methods. I.e., one method per supported output type.

* To support different use cases and to keep the API extensible, the
  sanitization should be configurable via an options dictionary.

  * The default (without configuration) should provide safety against script
    execution.

* To make it easy to review and reason about sanitizer configs, there should
  be sanitizer instances for a given configuration.

  * DOMPurify supports per-call and a global "default" config. Global
    configuration state can be awkward to use when different dependencies
    have different ideas about what the global state should be. Likewise,
    per-call configs can be error prone and hard to reason about, since every
    call site might be a little different.

* There seem to be a handful of common use cases. There should be sensible
  default options for each of these.

### Proposed API

The basic API would be`.sanitize(value)` to produce a DocumentFragment.
Sanitizers can be constructed with a dictionary of options.

```
[
  Exposed=Window,
  SecureContext
] interface Sanitizer {
  constructor(optional SanitizerConfig config = {});
  DocumentFragment sanitize(DOMString input);

  DOMString sanitizeToString(DOMString input);
  readonly attribute SanitizerConfig creationOptions;
}
```

### Example usage

A simple web app wishes to take a string (say: a name) and display it on
the page:

```
const s = new Sanitizer();
const node = document.getElementById("...");

node.innerText = "";
node.appendChild(s.sanitize(user_supplied_value));
```


### Roadmap

* Sanitizer Specification 1.0
  * Supports config-less sanitization;
  * Supports customization of allowlists for elements and attributes;
  * The core goal is the sanitization of any markup that can cause XSS.

* Sanitizer Specification 2.0
  * Supports additional configuration options, possibly stemming from DOMPurify;
  * Supports custom callbacks and hooks to fine-tune sanitization results.

## FAQ

### Who would use this and why?
* Web application developers who want to allow some - but not all - HTML. This could mean developers handling Wiki pages, message boards, crypto messengers, web mailers, etc.
* Developers of browser extensions who want to secure their applications against malicious user-controlled, or even site-controlled, HTML.
* Application developers who create Electron applications and comparable tools which interpret and display HTML and JavaScript.

### Wouldn’t this be just a niche feature?
* No, according to the statistics offered by the npm.js platform, libraries such as DOMPurify are downloaded over 200 thousand times every month . DOMPurify is furthermore used from within various CDN networks for which no metrics are available at this point.
* Besides web applications, sanitizer libraries are also used in Electron applications, browser extensions and other applications making use of a browser engine.

### But this can be done on the server, can’t it? Like in the “olden days”.
* While this is correct, server-side sanitizers have a terrible track record for being bypassed. Using them is conducive to a Denial of Service on the server and one simply cannot know about the browser’s quirks without being highly knowledgeable in this particular realm.
* As a golden rule, sanitization should happen where the sanitized result is used, so that the above noted knowledge gaps can be mitigated and various risks might be averted.

### What are the key advantages of Sanitizing in the browser?
* *Minimalistic Approach:* Various libraries, such as DOMPurify, currently need to work around browser-specific quirks. This would no longer matter had the implementations become directly embedded in the browser.
* *Simplicity:* This approach does not aim to create any additional complexity, introduce new data types, labels or flags, it simply aims to provide an API that allows developers to take an untrusted string, remove anything that can lead to script execution or comparable and retuirn the sanitized result, again as a string (see also [#4](https://github.com/WICG/sanitizer-api/issues/4)).
* *Bandwidth:* Sanitizer libraries are “heavy” and by reducing the need to pull them from a server by embedding them in the browser instead, bandwidth can be saved.
* *Performance:* Sanitizing markup in C/C++ is faster than doing the same in JavaScript.
* *Reusability:* Once the browser exposes a sanitizer in the DOM, it can be reused for potentially upcoming [SafeHTML](https://lists.w3.org/Archives/Public/public-webappsec/2016Jan/0113.html) implementations, [Trusted Types](https://github.com/WICG/trusted-types), secure elements and, if configurable, even be repurposed for other changes in the user-controlled HTML, for instance in connection with URL rewriting, removal of annoying UI elements and CSS sanitization.

### What if someone wants to customize the sanitization rules?
* It should be trivial to implement basic configuration options that allow customization of the default allowlist and enable developers to remove, add or completely rewrite the allowed elements and/or attributes.
* The already mentioned browser's clipboard sanitizer already ships an allowlist, so the only task would be to make it configurable.

### Isn’t building a sanitizer in the browser risky and difficult?
* No, it may appear so but, in fact, the browsers already feature at least one sanitizer, for instance the one handling HTML clipboard content that is copied and pasted across origins. The existing puzzle pieces only need to be put correctly together in a slightly different way before they are then exposed in the DOM.
* If there are any risks connected to the new process, then they are not new but rather already concern the handling of the user-generated HTML presently processed by the in-browser sanitizers. Aside for configuration parsing, which should be a trivial problem to solve, no added risks can be envisioned.

### Wait, what does secure even mean in this context?
* Calling the process secure means that a developer can expect that XSS attacks caused by user-controlled HTML, SVG, and MathML are eradicated.
* The sanitizer would remove all elements that cause script execution from the string it receives and returns.

