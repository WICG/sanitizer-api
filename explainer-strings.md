# HTML Sanitizer API Explainer: Strings in HTML Sanitizer API

The HTML Sanitizer API offers seperate methods to sanitize node-to-node and
string-to-node. This may be surprising, as many
HTML Sanitizer libraries offer string-to-string APIs as their main or even
only API. This explainer gives a bit of background of what HTML Sanitizer
API offers with respect to HTML strings, and why.

## Three Use Cases

Sanitization in the context of a browser's DOM can be thought of as three
seperate steps:

1. Taking a string and parsing it into HTML elements. (Plus text nodes, etc.)
2. Removing nodes from that tree which are undesireable.
3. Integrating the resulting tree into the live DOM.

Many sanitizing libraries perform steps 1 + 2 and then serialize the resulting
node tree back into a string. The developer can then use this string and insert
it into the DOM, either by assigning to `Element.innerHTML`, or maybe via the
`DOMParser` or `Node.appendChild` APIs, which the browser will then implement
by parsing the string into HTML elements again.

This arrangment is flexible and easy to use, but it has two downsides:
It is inefficient, since we first serialize and then re-parse the
sanitization result. These are two heavy-weight operations that invert each
other, which means we could choose not to do either. And worse, serializing
and re-parsing aren't _exact_ inverses of each other, which may cause subtle
bugs to creep in when re-parsing HTML content. A specific class of such bugs,
called mutated XSS or mXSS for short, allows script content to be passed
through those operations, thus undoing the security benefit we had hoped to
gain from sanitization in the first place.

The HTML Sanitizer API is written to give the developer flexibility, while
avoiding these problems. The string handling of the HTML Sanitizer API revolves
around three use cases:

### Case 1: Sanitizing with DOM Nodes, Only.

If the data to sanitize is already available as DOM nodes - for example
a `Document` instance in a frame - then the `Sanitizer.sanitize` method can
be used. This would not use any string-based functionality at all.

### Case 2: Sanitizing & Set a String with Implied Context

If the data to sanitize is available as a string and if it is going to
be inserted into the DOM right after sanitization, then the `Element.SetHTML`
method can do both steps at the same time.

### Case 3: Sanitizing a String with a Given Context

If the data to sanitize is available as a string, but it is undesired (or not
possible) to insert it into the DOM at the point of sanitization, then
the `Sanitizer.sanitizeFor` method can be used. This requires the developer
to supply the context in which the result is going to be used.

## But Why?

Early versions of the HTML Sanitizer API supported a
`Sanitizer.sanitizeToString(DOMString)` method. After much deliberation this
was removed in favour of the current API. There were several,
interlocking concerns that resulted in a changed API:

### Performance

Parsing and serializing HTML are expensive operations. Since the core sanitizer
algorithm operates on a DOM tree, the "usual" serializing and eventual
re-parsing operations are simply wasteful, since the exact same result can be
obtained by ... not doing either step in the first place. So if we can
structure our API to not return strings, then we can just avoid re-parsing
entirely.

### Parsing HTML Strings Requires Context

Parsing fragments of HTML is impossible. That is: Parsing HTML without a
given context is impossible. This may sound surprising, but parsing HTML
strings is defined exclusively with a given context element. It's impossible
to parse an HTML string by itself; the HTML parser must know which context
to use.

If one attempts parsing without a context - say a library offers such
functionality - then this usually means a non-standards compliant library,
or an "implied" context, which probably will not match the context of the
actual use. This runs the risk that the actual parsing result that the browser
does, e.g. when assigning to `Element.innerHTML`, will be different.

What difference does the context make?

A simple example is the handling of table data (`<td>`) inside a table
and non-table context. If the strinng `"<td>text</td>"` is passed to
the `.innerHTML` accessor of either a `<table>` or `<div>` element, then
the `<td>` element would be parsed for the former, but would be dropped
for the latter case.

### mXSS Attacks: Abusing Re-Parsing and Parse Context Mismatches

Here is a more complex example:

```
<form><math><mtext></form><form><mglyph><style></math><img src onerror=alert(1)>
```

This example was brought to us by CVE-2020-26870, which has the advantage of [a
very nice writeup by the security researcher who discovered it](https://research.securitum.com/mutation-xss-via-mathml-mutation-dompurify-2-0-17-bypass/).
For details, we encourage the reader to follow the link

The gist is that this string will change its meaning when being re-parsed. It
has been carefully crafted to have one interpretation when parsed, and another
one when being re-parsed, after having been parsed and serialized previously.
Note that it contains a `<style>` element. On the initial parse, the `<img>`
element, which contains an event handler, is inside the `<style>` element and
is thus being parsed as a (malformed) stylesheet. On the second parse, it
will be parsed as a regular element, with an event handler.

If this example is being presented to a sanitizer library, the sanitizer will
see the result of the first pass, and will let the "event handler" - which it
sees as style-sheet content - pass. If this is being re-parsed on inserting
this into the DOM, the DOM parser will in turn see a regular element with an
event handler.

This kind of parse/re-parse mismatch (and its cousin, the parse context
mismatch) has let to a number of attacks to bypass sanitizing libraryies,
collectively known as mXSS.

### Putting the Pieces Together: A New, Safer, and More Efficient API

When contemplating these three concerns, we decided to
reformulate the Sanitizer API along these rules:

- The API will return the DOM tree it operates on, thus discouraging re-parsing
  in general.
- All string-based operations require a context node that will be used for
  HTML parsing.
- The API will preserve the context information, and won't hide it. Either
  the API operates on the context node directly, or it will pass
  along the context node in the result.

This leads to the current API:

For `Sanitizer.sanitize`, no strings and therefore no HTML parsing are
involved. It does not require a parsing context. It returns a modified copy
of the input.

For `someElement.setHTML`, the context node is the `this` element that it is
being called on. It returns no result at all, and instead the operation will
commence on the `this` node.

For `Sanitizer.sanitizeFor`, the developers will have to tell the Sanitizer
what context they'd like to use the result in. The return value will contain
both the result, and a newly created element that acts as the context node.
Conveniently, a container for these two values already exists: It's the elment
node itself. Hence we return it, with the sanitized input as the children of the
newly created context element.

### An Escape Hatch

What if a developer wishes to have a string-to-string API after all? Maybe
because an existing code base was built around the assumption of a
string-to-string sanitization library, and it isn't easy to refactor?

The `Sanitizer.sanitizeFor`method provides an escape hatch:
`.sanitizeFor(value, context).innerHTML`.

Given a suitable `context`, querying `.innerHTML` on the result of
`Sanitizer.sanitizeFor` will retrieve the string result the developer
presumably expects.  However, we recommend against this practice, as this
opens up the app to context- and re-parse-mismatches and therefore mXSS
attacks, and puts the burden to ensure safe usage entirely on
the developer.

# Please Try it Out

Please [try out the Sanitizer API](https://sanitizer-api.dev/?).
The [FAQ shows how to enable it in current
browsers](https://github.com/WICG/sanitizer-api/blob/main/faq.md#can-i-use-the-sanitizer-in-my-app). Issues and suggestions can be reported on
[GitHub](https://github.com/WICG/sanitizer-api/issues).
