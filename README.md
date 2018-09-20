# Sanitization Explainer

## The Problem

Various web applications often need to work with strings of HTML on the client-side. This might take place, for instance, as part of a client-side templating solution or perhaps come to play through the process of rendering user-generated content. The key problem is that it remains difficult to perform these tasks in a safe way. This is specifically the case because the naive approach of joining strings together and stuffing them into an [Element](https://dom.spec.whatwg.org/#element)'s [`innerHTML`](https://w3c.github.io/DOM-Parsing/#widl-Element-innerHTML) is fraught with risks. A very common negative implication concerns the JavaScript execution, which can occur in a number of unexpected ways.

To address the problem, libraries like [DOMPurify](https://github.com/cure53/DOMPurify) attempt to carefully manage the inputs and alleviate risks. This is usually accomplished through parsing and sanitizing strings before insertion and takes advantage of a white-list for constructing a DOM and handling its components. This is considerably safer than doing the same on the server-side, yet much untapped potential can still be observed when it comes the client-side sanitization.

As it stands, every browser has a fairly good idea of when and how it is going to execute code. Capitalizing on this, it is possible to improve the user-space libraries by teaching the browser how to render HTML from an arbitrary string in a safe manner. In other words, we seek to make sure that this happens in a way that is much more likely to be maintained and updated along with the browsers’ ever-changing parser implementations.

## The Proposal

Broadly speaking, the sanitizers already exist as third-party libraries (e.g. DOMPurify, see also the [paper](https://www.researchgate.net/publication/319071617_DOMPurify_Client-Side_Protection_Against_XSS_and_Markup_Injection)) or in browser-specific and proprietary APIs (e.g. toStaticHTML). The browser-agnostic libraries achieve the goal by relying on the HTML parsing found in-browser, as exposed through [`createHTMLDocument`](https://developer.mozilla.org/en-US/docs/Web/API/DOMImplementation/createHTMLDocument) or [`DOMParser`](https://developer.mozilla.org/en-US/docs/DOM/DOMParser). Conversely, they still have to work around browser-specific quirks. An API that is built into the browser should be seen as being at the very best place for guaranteeing a properly sanitized markup. 

### Two approaches for achieving the desired functionality

While the final syntax of the API has not yet been decided on, we suggest two possible approaches for the developers willing to use the browser-embedded sanitizer.

*Option 1. A simple, no-config approach to sanitizing into a secure default quickly and easily.*

```javascript
let dirty = user_controlled_html;
someElement.innerHTML = sanitize(dirty);
```

In this example, the developer would simply pass a string of dirty HTML into the sanitizer and receive the sanitized result as another string. After that, the received string can be safely written into the DOM. The browser would make use of a whitelist by default. This approach is inspired by Microsoft’s toStaticHTML.

*Option 2. A re-usable sanitizer that implements configurable behaviors.*

```javascript
let sanitizer = new Sanitizer(options);
let dirty = user_controlled_html;
let someElement = document.getElementById(...);
let someOtherElement = document.getElementById(...);
clean = sanitizer.sanitizeToString(dirty);
someElement.innerHTML = clean;
// some place else
someOtherElement.appendChild(sanitizer.sanitizeToDocumentFragment(dirty));
```

In this approach, the developer creates an object for the sanitizer and this can be used multiple times with the same developer-provided configuration. It can be approached literally or with a simple use of the browser’s default config. Neither of the two suggestions poses compatibility risks, meaning that they both interoperate nicely with the existing DOM APIs as long as the whitelist is shared among all implementing browsers.

### Browser-Whitelists

To achieve the goal of a secure sanitization result, the browser needs to use a thoroughly battle-tested whitelist. This doesn’t reinvent the wheel as any given browser already knows the concept of a whitelist in the context of eliminating XSS, for example in, clipboard sanitization, sanitization of Chrome’s context views and similar. The general approach can simply be reused. 

What is more, the existing JavaScript libraries, such as DOMPurify, also ship well-tested and proven whitelists of elements and attributes that can be allowed by default.

### Roadmap

* Sanitizer Specification 1.0
  * Supports config-less sanitization;
  * Supports customization of whitelists for elements and attributes;
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
* *Bandwidth:* Sanitizer libraries are “heavy” and by reducing the need to pull them from a server by embedding them in the browser instead, bandwidth can be saved.
* *Performance:* Sanitizing markup in C/C++ is faster than doing the same in JavaScript.
* *Reusability:* Once the browser exposes a sanitizer in the DOM, it can be reused for potentially upcoming [SafeHTML](https://lists.w3.org/Archives/Public/public-webappsec/2016Jan/0113.html) implementations, [Trusted Types](https://github.com/WICG/trusted-types), secure elements and, if configurable, even be repurposed for other changes in the user-controlled HTML, for instance in connection with URL rewriting, removal of annoying UI elements and CSS sanitization.

### What if someone wants to customize the sanitization rules?
* It should be trivial to implement basic configuration options that allow customization of the default whitelist and enable developers to remove, add or completely rewrite the whitelisted elements and/or attributes. 
* The already mentioned browser's clipboard sanitizer already ships a whitelist, so the only task would be to make it configurable.

### Isn’t building a sanitizer in the browser risky and difficult?
* No, it may appear so but, in fact, the browsers already feature at least one sanitizer, for instance the one handling HTML clipboard content that is copied and pasted across origins. The existing puzzle pieces only need to be put correctly together in a slightly different way before they are then exposed in the DOM.
* If there are any risks connected to the new process, then they are not new but rather already concern the handling of the user-generated HTML presently processed by the in-browser sanitizers. Aside for configuration parsing, which should be a trivial problem to solve, no added risks can be envisioned.

### Wait, what does secure even mean in this context?
* Calling the process secure means that a developer can expect that XSS attacks caused by user-controlled HTML, SVG, and MathML are eradicated. 
* The sanitizer would remove all elements that cause script execution from the string it receives and returns.

