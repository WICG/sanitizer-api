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

> [!Note] The 'unsafe' methods are being worked on here: https://github.com/whatwg/html/pull/9538

## Major differences to previously proposed APIs:

The currently proposed API differs in a number of aspects:

- Two sets of methods, `innerHTML`-like and `DOMParser`-like.
- Since the 'sanitizer' config can now be used in both safe and unsafe ways,
  it's arguably no longer a sanitizer config but a filter config.
- Enforcement of a security baseline depends on the method. The filter/sanitizer
  config can now be used differently, either in a guaranteed-secure way or in
  use-config-as-written way.
- The configuration dictionary differs substantially in syntax.

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

### Parsing in XML documents

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

### Safe vs Unsafe methods

The "safe" methods remove all script-y content defined by the platform and
let the rest pass:

```js
element.setHTML(`<a href=about:blank onclick=alert(1) onload=alert(2) id=myid class=something><script>alert(3);</script>`);
// <div><a href="about:blank" id="myid" class="something"></a></div>
```

Note that the context node might also be a script element. In this case adding
plain text to it creates new script content:

```js
const sneaky = document.createElement("script");
sneaky.setHTMLUnsafe("alert('Surprise!');");
// <script>alert('Surprise!');</script>
```

For the "safe" versions this case will be treated specially. `setHTML` checks
the context element and calling it on a `<script>` element is a no-op.

```js
sneaky.setHTMLUnsafe("boring();");  // <script>boring();</script>
sneaky.setHTML("alert('Surprise!');");  // <script>boring();</script>
```

### Configuration Options: Basic use and namespaces

The operation of the built-in sanitizer can be configured to suit your
applications' needs. Both "safe" and "unsafe" versions can take a configuration.

The "safe" version will ignore configuration items that break its security
guarantees:
```js
const an_unsafe_config = new Sanitizer({ 'elements': [ { name: 'script' } ] });
element.setHTML("<script>", { sanitizer: an_unsafe_config });  // <div></div>
element.setHTMLUnsafe("<script>", { sanitizer: an_unsafe_config });  // You now have a script. Congrats.
```

For elements the HTML namespace is default. For attributes, the null namespace.
Other namespaces can be supported. A string entry stands for a dictionary with
only the name, in the HTML/null namespace (for elements/attributes,
respectively).

``` js
const config_with_namespaces = new Sanitizer({
  elements: [
    'a',  // The HTML anchor element.
    { name: 'a' },  // Also the HTML anchor element.
    { name: 'a', namespace: 'http://www.w3.org/1999/xhtml' },  // Another one.
    { name: 'a', namespace: 'http://www.w3.org/2000/svg' }  // SVG's anchor element
  ],
  attributes: [
    'href',  // An href attribute. The one you'd expect on an HTML anchor.
    { name: 'href' },  // The very same.
    { name: 'href', namespace: '' },  // There it is again.
    { name: 'href', namespace: 'http://www.w3.org/1999/xlink' },  // xlink:href. SVG sometimes uses this.
    { name: 'href', namespace: 'http://www.w3.org/1999/xhtml' }  // This isn't a thing.
        // It won't match any HTML-defined href attributes. Probably the config
        // author made an error.
  ]
});
```

> [!NOTE]
> The `config_with_namespaces` example contains multiple entries for the same
> element or attribute, to illustrate the syntax. Note that this isn't actually
> allowed.

### Configuration Options: Sanitizer object or dictionary.

The Sanitizer object can be constructed from a dictionary. The same dictionary
can also be used directly in the method options.

```
const config_dict = {
  elements: [ "div", "p", "em", "b", "span" ],
  attributes: [ "class", "style" ]
};

// These two should be the same:
const some_html_string = "...";
div.setHTML(some_html_string, {sanitizer: config_dict});
div.setHTML(some_html_string, {sanitizer: new Sanitizer(config_dict)});
```

Note that implementations are expected to perform normalization work on the
configuration, which can be easily re-used and amortized over many calls when
used with the Sanitizer object that holds the configuration. To encourage this
usage we explicitly instantiate objects in this explainer, outside of this
particular sub-section.

```
// These should have the same results, but likely different performance:
const huge_array_of_strings = [ "...", ... ];

for (const str of huge_array_of_strings) {
  div.setHTML(str, {sanitizer: config_dict});
}

const sanitizer = new Sanitizer(config_dict);
for (const str of huge_array_of_strings) {
  div.setHTML(str, {sanitizer: sanitizer});
}
```

### Configuration Options: Allowing or removing elements or attributes

There are two ways you can build up a config: Specify the elements & attributes
you wish to allow. This is easy to read and makes it easy to understand what
to expect in the sanitizer output. Or you can specify what elements & attributes
you wish to remove. Or to block, as other sanitizer libraries might call it.
This effectively specifies the sanitizer output relative to the built-in list.
This can be useful if you wish to mostly retain the built-in defaults.

```js
const config_allow_some_formatting = new Sanitizer({
  elements: [ "div", "p", "em", "b", "img" ],  // Allows only 5 elements.
  attributes: [ "class" ]  // Allows only class attributes.
      // Output with "safe" and "unsafe" methods are the same for this config.
});
const config_disallow_style_definitions = new Sanitizer({
  removeElements: [ "style" ],  // Allows the defaults, but without <style>.
  removeAttributes: [ "class", "style" ]  // No style or class attribute either.
      // And not XSS-y stuff, either, if used with a "safe" method.
      // Output with "safe" and "unsafe" methods might be quite different.
});
```

You may also wish to remove elements, but retain their children. This is
chiefly useful to remove unwanted formatting from user input, while
preserving its textual content.

```js
const config_that_removes_elements_but_preserves_their_children = new Sanitizer({
 replaceWithChildrenElements: ["span", "em", "u", "s", "i", "b"]
});

element.setHTML(
  "Fancy <b>text</b> with <span style='color:blue'>pizzazz</span>.",
  { sanitizer: config_that_removes_elements_but_preserves_their_children });
  // <div>Fancy text with pizzazz.</div>
```

There is no `replaceWithChildrenAttributes` because attribute nodes do not have
children.

`replaceWithChildrenElements` applies to its immediate children, i.e. to one
level. Combining `elements` with `replaceWithChildrenElements` lets you keep
some formatting, but all the text content:

```js
const config_replace_spans = new Sanitizer({
  elements: ["b", "i"],
  replaceWithChildrenElements: ["span"]
});

// <div>Fancy text with <b>pizzazz</b>.</div>
element.setHTML(
  "Fancy <span style='color:blue'>text with <b>pizzazz</b></span>.",
  { sanitizer: config_replace_spans}
);
```

### Configuring attributes per element

A common use case is to allow or remove all instances of a given attribute,
but this isn't always sufficient. Attribute interpretation depends on the
element they are attached to, and so one may also want to act on attributes
on specific elements.

In the example `config_allow_some_formatting` in the previous chapter
we have allowed the `class` attribute on any of allowed elements.
If one wanted to allow `class` everywhere, but `src` only on `<img>`, the
following would do:

```js
const config_with_element_specific_attributes = new Sanitizer({
  elements: [
    "div", "p","em", "b",
    { name: "img", attributes: [ "src" ] }
  ],
  attributes: ["class"],
});
```

If you want to remove `src` attributes from `<input>` elements but retain them
elsewhere, you can use:

```js
const remove_src_attribute_from_input = new Sanitizer({
  elements: [{ name: "input", removeAttributes: ["src"]}],
});
```

Note that the `removeAttributes` key is on an allowed element, since removing
the element itself would also remove all the attributes that are part of that
element.

### Comments

Handling of HTML comment nodes can be controlled by an option. Setting
`comments` to `true` allows them:

```js
const config_comments: new Sanitizer({ comments: true });
element.setHTML("XXX<!-- Hello world! -->XXX", {sanitizer: config_comments});
// <div>XXX<!-- Hello world! -->XXX</div>
```

### Modifying Existing Configurations

The `Sanitizer` object offers multiple methods to easily modify or tailor
an existing configuration. The query methods (`get()` and `getUnsafe()`) can
be used to retrieve a dictionary representation of a Sanitizer,
for introspection, or for use with the Sanitizer constructor to create a new
Sanitizer. Additionally, there are methods that directly manipulate the filter
functionality of the Sanitizer.

The following methods are offered on the Sanitizer object:

- `allow(x, options)`
  - `options` is an optional dictionary argument.
    Supported keys are: `"attributes":` and `"removeAttributes":.`
- `removeElement(x)`
- `replaceWithChildren(x)`
- `allowAttribute(x)`
- `removeAttribute(x)`

These correspond 1:1 to the keys in the configuration dictionary.

Adding an element or attribute to any of the allow- or deny-lists will also
remove that element or attribute from the other lists for its type. E.g.,
calling `allow(x)` will also remove `x` from the removeElements and
replaceWithChildrenElements lists.

Any name can be given as either a string, or a dictionary with name or
namespace, just as with the configuration dictionary.

```js
const s = new Sanitizer({ elements: ["div", "p", "b"] });
s.element("span");
s.removeElement("b");
s.get();  // { elements: ["div", "p", "span"], removeElements: ["b"] }
          // Really, all these entries will be dictionaries with name and
          // namespace entries.
```

### Configuration Errors

The configuration allows expressing redundant or even contradictory options.
For example, allowing and removing the same element. In cases where the
meaning of a configuration dictionary isn't clear, we will
throw a `TypeError` instead of making a best effort attempt at interpreting
the configuration. A well-formed configuration has the following properties:


* It contains either an allow-list or a remove-list, but not both.
  * This applies to both element and attribute lists, seperately.
  * Note that any config with both, an allow-list and remove-list, can be
    rewritten by removing the remove-list items from the allow-list and then
    droping the remove-list entirely.
  * Both allow-lists and remove-lists can be combined with
    replace-with-children-lists.
* The action for any name - allow, remove, or replaceWithChildren - should be
  specified only once. E.g. an element name should neither appear twice in an
  allow-list, nor should it appear in both an allow-list and a
  replace-with-children-list.
  * This would apply to short forms as well.
    E.g., `["div", { name: "div", namespace: "http://www.w3.org/1999/xhtml" }]`
    contains the same name twice and would thus throw.
  * While lists with duplicate element or attribute names could be coalesced,
    it is ambiguous what the meaning of duplicate elements with different
    element-dependent attribute lists would be.
* The name must be set.

```js
// Mixing allow and block lists throws.
const config_that_mixes_allow_and_block_lists = new Sanitizer({
    elements: ["i", "u"],
    removeElements: ["u", "s"],
});
element.setHTML("bla", {sanitizer: config_that_mixes_allow_and_block_lists}); // throws

// Mixing allow and replace with children lists works.
const config_that_retains_simple_styling_but_most_text = new Sanitizer({
  elements: ["p", "b", "i"],
  replaceWithChildrenElements: ["div", "span", "em", "u", "s", "li"],
});
const styled_text = "<p>Some <span style='color: blue'>colourful</span> <u>styled</u> <b>text</b>";

// <div><p>Some colourful styled <b>text</b></p></div>
element.setHTML(styled_text, {sanitizer: config_that_retains_simple_styling_but_most_text});

// Duplicate entries throw.
const config_with_dupes = new Sanitizer({
  elements: [ "div", { name: "div", namespace: "http://www.w3.org/1999/xhtml" } ]
});
element.setHTML("bla", {sanitizer: config_with_dupes});  // throws.

const config_with_dupes2 = new Sanitizer({
  elements: [
    { name: "div", attributes: ["class"] },
    { name: "div", attributes: ["style"] }
  ] });
element.setHTML("bla", config_with_dupes2);  // throws.
```

Listing an attribute in the "global" allow-list and in an element specific one
is allowed. In this case, the specific action takes precedence.

```js
const config_with_local_and_global_attributes = new Sanitizer({
  elements: [ "span", { name: "b", removeAttributes: [ "class" ] } ],
  attributes: ["class"]
});

// <div><span class="a">abc</span> <b>def</b></div>
element.setHTML("<span class='a'>abc</span> <b class='b'>def</b>",
                {sanitizer: config_with_local_and_global_attributes});
```

### Querying the Configuration

If you would like to better understand what a given configuration will do, you
can query a `Sanitizer` (and possibly build a new config out of an existing one):

```js
const a_simple_config = new Sanitizer({ elements: [ "div", "p", "span", "script" ] });

a_simple_config.get();
// The result will be quite long. It'll look something like this:
{
  elements: [
    { "name": "div", "namespace": "http://www.w3.org/1999/xhtml" },
    { "name": "p", "namespace": "http://www.w3.org/1999/xhtml" },
    { "name": "span", "namespace": "http://www.w3.org/1999/xhtml" }
  ],
  attributes: [
    { "name": "href", "namespace": "" },
    { "name": "class, "namespace": "" },
    { "name": "id", "namespace": "" },
    // ... many more
  ]
};
```

Note that:

1. The returned config entries all have the "long" form with explicit name
   and namespace.
1. The `"script"` element has disappeared. Because, when used in a "safe"
   version of the API, it wouldn't be allowed.
1. Note that we suddenly have an `"attributes"` key that
   represent the defaults.

But what would the unsafe versions do with this config? Just ask:

```js
a_simple_config.getUnsafe();
// The result:
{
  elements: [
    { "name": "div", "namespace": "http://www.w3.org/1999/xhtml" },
    { "name": "p", "namespace": "http://www.w3.org/1999/xhtml" },
    { "name": "span", "namespace": "http://www.w3.org/1999/xhtml" }
    { "name": "script", "namespace": "http://www.w3.org/1999/xhtml" }
  ],
  attributes: [
    // ... many more. Should be the same list as above.
  ]
};
```

The configuration that is returned corresponds to what the specification calls
a canonical configuration: Names are resolved into their explicit name &amp;
namespace form. But some keys are also processed further. For example:

```js
new Sanitizer({
  removeElements: [ "span" ],
  removeAttributes: ["id", "class"]
}).get();

// The result will be quite long. It'll look something like this:
{
  elements: [
    { "name": "div", "namespace": "http://www.w3.org/1999/xhtml" },
    { "name": "p", "namespace": "http://www.w3.org/1999/xhtml" },
    // ... many more. But no span.
  ],
  attributes: [
    { "name": "href", "namespace": "" },
    // ... many more. But no id or class.
  ]
};
```

Note that here, the remove-lists are converted to their allow-list equivalents,
based on the built-in defaults.
