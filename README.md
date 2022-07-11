# Sanitizer API

The *Sanitizer API* is a proposed new browser API to bring a safe and
easy-to-use capability to sanitize HTML into the web platform.

Status:

* The Sanitizer API is currently being incubated in the
  [Sanitizer API](https://github.com/WICG/sanitizer-api) [WICG](https://wicg.io/),
  with the goal of bringing this as a standard into the
  [W3C WebAppSec Working Group](https://www.w3.org/2011/webappsec/).
* Early implementations are available in [select web browsers](#Implementations).
* The API is not finalized and still subject to change.

Here you can find additional information:

* The [draft specification](https://wicg.github.io/sanitizer-api/).
* A list of [questions & answers](faq.md).
* [MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API).
* Implementation Status:
  * [Mozilla position](https://github.com/mozilla/standards-positions/issues/106),
    [Chrome Status](https://www.chromestatus.com/feature/5786893650231296),
    [WebKit position](https://lists.webkit.org/pipermail/webkit-dev/2021-March/031738.html).
  * [Can I use 'Sanitizer API'](https://caniuse.com/mdn-api_sanitizer)?
  * [Web Platform Tests](https://wpt.fyi/results/sanitizer-api?label=experimental&label=master&aligned)
    ([test source](https://github.com/web-platform-tests/wpt/tree/master/sanitizer-api)).
* The [Sanitizer API Playground](https://sanitizer-api.dev) is an easy way to
  play with the API, if it's enabled in your browser.
* An early [W3C TAG review](https://github.com/w3ctag/design-reviews/issues/619).
* The [original explainer](explainer.md) goes into more detail about why
  we are proposing this as a new standard (rather than a library). The API
  proposed there is a little outdated, however.

## Implementations

If you wish to try out early Sanitizer implementations, the
[FAQ](faq.md#can-i-use-the-sanitizer-in-my-app) has you covered:

> Firefox: Go to about:config, search for the dom.security.sanitizer.enabled flag and set it to true
>
> Chromium / Chrome: Start the browser with the --enable-blink-features=SanitizerAPI flag.

## Explainer

The core API of the Sanitizer is rather simple: There are `Sanitizer` objects,
and they have a `.sanitize` method that produces a `DocumentFragment` from a
given text string. Or from another `DocumentFragment`, or even from a whole
`Document`.

Example:
```js
  // Every webapp has to deal with untrusted input in some form. It could be
  // data off the network; from query parameters; any user inputs; or
  // (sometimes) even from ones own server. Here, we use the simplest form as
  // an example and get data right out of a <textarea> element:
  const untrusted_input = document.querySelector("textarea").textContent;

  // In most cases, we don't want the user input to contain any markup anyhow,
  // in which case the easiest and best method is to just assign it to
  // another .textContent:
  document.querySelector( ...something... ).textContent = untrusted_input;

  // But what if want (some) markup? Then, sanitize it before use. The result
  // might be ugly, or contain curse words, but it won't contain any script:
  const sanitizer = new Sanitizer();
  document.querySelector( ...something... ).setHTML(
      untrusted_input, {sanitizer: sanitizer});

  // Sanitizer is safe by default, so the default instance will already do the
  // job:
  document.querySelector( ...something... ).setHTML(untrusted_input);

  // All of these values for untrusted_input would have had the same result:
  // <em>Hello World!</em>
  const elem = document.querySelector( ...something... )
  elem.setHTML("<em>Hello World!</em>");
  elem.setHTML(""<script src='https://example.org/'></script><em>Hello World!</em>");
  elem.setHTML(""<em onlick='console.log(1)'>Hello World!</em>");
```

Oftentimes, applications have additional &mdash; often stricter &mdash;
requirements beyond just script execution. For example, in a certain context
an application might want to allow formatted text, but no structural or other
complex markup. To accommodate this, the API allows for creation of multiple
`Sanitizer` instances, which can be customized on creation.

Example:
```js
  // We must sanitize untrusted inputs, but we may want to restrict it further
  // to meet other, related design goals. Here, we'll have one Sanitizer only
  // for scripting, and then another that allows for character-level formatting
  // elements, plus the class= attribute on any element, but nothing else.
  const sanitizer = new Sanitizer();
  const for_display = new Sanitizer({
    allowElements: ['span', 'em', 'strong', 'b', 'i'],
    allowAttributes: {'class': ['*']}
  });

  const untrusted_example = "Well, <em class=nonchalant onclick='alert(\'General Kenobi\');'><a href='https://obiwan.org/home.php'>hello there<a>!"

  // Well, <em class="nonchalant"><a href='https://obiwan.org/home.php'>hello there<a>!</em>
  elem.setHTML(untrusted_example, {sanitizer: sanitizer});
  elem.setHTML(untrusted_example);  // Same, since it uses a default instance.

  // Well, <em class="nonchalant">hello there!</em>
  elem.setHTML(untrusted_example, {sanitizer: for_display});

  // The following code will insert our untrusted_example into a block element
  // we have picked for this purpose. We can be sure that it won't contain
  // script, and we can also be sure that it contains no block-level markup
  // or more.
  document.querySelector("p.out").setHTML(untrusted_example, {sanitizer: for_display});
```

It is the overarching design goal of the Sanitizer API to be safe and simple,
at the same time. Therefore the API is not only safe by default, but is also
perma-safe. The Sanitizer will enforce a baseline that does not allow script
execution, even if a developer may have inadvertently configured script-ish
elements or attributes to be supported.

Example:
```js
  const misconfigured = new Sanitizer({
    allowElement: ["s", "strike", "span", "script"],
    allowAttributes: {"class": ["*"], "style": ["span"], "onclick": ["*"]}
  });

  const untrusted_input = "<span onclick='2+2'>some</span><script>2+2</script>thing";
  // <span>some</span>thing
  elem.setHTML(untrusted_input, {sanitizer: misconfigured});
```

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

-----------------
[![Build Status](https://travis-ci.org/WICG/sanitizer-api.svg?branch=main)](https://travis-ci.org/WICG/sanitizer-api)
