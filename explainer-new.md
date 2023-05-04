# Sanitizer API: New API Explainer

Context: Various disagreements over API details lead to a re-design of the
Sanitizer API. The current (April '23) spec draft no longer represents a
consensus within the Sanitizer working group (or other interested groups, like
the HTML WG). This explainer sketches out a new API design:

## A new proposal, based on #192:

There is a 2x2 set of methods that parse and filter the resulting node tree:
On one axis they differ in the parsing context and are analogous to `innerHTML`
and `DOMParser.parseFromString`, respectively; on the other, they differ in
whether they enforce an XSS-focused security baseline or not. These two aspects
pair well and yield:

- `Element.setHTML(string, {options})` - Parses `string` using `this` as
  context element, like assigning to `innerHTML` would ; applies a filter,
  while enforcing an XSS-focused baseline; and finally replaces the children
  of `this` with the results.
- `Element.setHTMLUnsafe(string, {options})` - Like above, but it does not
  enforce a baseline. E.g. if the filter is configured to allow a `<script>`
  element, then a `<script>` would be inserted.
- `Document.parseDocument(string, {options})` (static method) - Creates a new
  Document instance, and parses `string` as its content, like
  `DOMParser.parseFromString` would. Applies a filter, while enforcing an
  XSS-focused baseline. Returns the document.
- `Document.parseDocumentUnsafe(string, {options})` (static method) - Like
  above, but it will not enforce a baseline.

All variants take an options dictionary with a `filter` (naming TBD) key and a
filter configuration. The options dictionary can be easily extended to accept
whatever parsing parameters make sense.

## Major differences to current proposal(s):

- Two sets of methods, `innerHTML`-like and `DOMParser`-like.
- Enforcement of a security baseline moves to the method. The filter config -
  formerly the sanitizer config - can now be used in differently,
  either in a guaranteed-secure way or in use-config-as-written way.
- Since the 'sanitizer' config can now be used in both safe and unsafe ways,
  it's arguably no longer a sanitizer config but a filter config.

## Open questions:

- Defaults: If no filter is supplied, do the safe methods have any filtering
  other than the baseline? Do the unsafe methods have default filtering?
  (I.e., would they allow `<script>` by default, or would they drop `<script>`
  by default but allow it if specifically allow-listed.)
- Defaults: All of these are new methods, without legacy usage. Would DSD
  parsing default to `true`? Do we even decide that, or would we instead ask
  the HTML WG and adopt whatever their choice?
- Should the filter config be a separate object, or should it be a plain dictionary?
  - Reasons pro dictionary:
     - Simpler.
  - Reasons pro object:
     - Allows to pre-process of the config and to amortize the cost over many calls.
     - Allows adding other useful config operations, like introspection.
- Exact filter options syntax. I'm assuming this will follow the discussion in
  #181.
- Naming is TBD. I'm trying to follow the preferences from the recent 'sync' meeting.
- Baseline for safe methods: There are some "special" behaviours (currently in
  "handle funky elements"), mainly around dropping javascript:-URLs in contexts
  that navigate. Should this be available as an option (which would then be
  force-true for safe usage, and default-false but available for non-safe
  usage), or would that be custom behaviour only for the safe methods?
- Should the `DOMParser`-like methods offer a mimetype options, like DOMParser
  does?

## Examples
```js
// TODO
```
