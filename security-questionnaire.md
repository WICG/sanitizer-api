* What information might this feature expose to Web sites or other parties, and for what purposes is that exposure necessary?
This feature does not expose any new information.

* Do features in your specification expose the minimum amount of information necessary to enable their intended uses
This feature does not expose any new information.

* How do the features in your specification deal with personal information, personally-identifiable information (PII), or information derived from them?
This feature does not expose any new information.

* How do the features in your specification deal with sensitive information?
This feature does not submit or expose any information. It is merely operating on existing HTML.

* Do the features in your specification introduce new state for an origin that persists across browsing sessions?
This feature does not introduce new state.

* Do the features in your specification expose information about the underlying platform to origins?
This feature does not expose any new information.

* Do features in this specification allow an origin access to sensors on a user’s device
This feature does not talk to devices or grant access to them.

* What data do the features in this specification expose to an origin? Please also document what data is identical to data exposed by other features, in the same or different contexts.
The feature does not expose new data to an origin. It operates solely on data structures that can already exists within the origin, e.g. DOMStrings or DocumentFragments.

* Do feautres in this specification enable new script execution/loading mechanisms?
No.

* Do features in this specification allow an origin to access other devices?
No.

* Do features in this specification allow an origin some measure of control over a user agent's native UI?
No.

* What temporary identifiers do the feautures in this specification create or expose to the web?
The API does not use any temporary identifiers.

* How does this specification distinguish between behavior in first-party and third-party contexts?
The API does not operate on third-party contexts.

* How do the features in this specification work in the context of a browser’s Private Browsing or Incognito mode?
The DOM operations we specify are oblivious of the browsing mode and do not store any state in either.

* Does this specification have both "Security Considerations" and "Privacy Considerations" sections?
Only a Security Considerations sections. See https://wicg.github.io/sanitizer-api/#security-considerations

* Do features in your specification enable origins to downgrade default security protections?
No. The feature requires a Secure Context.

* What should this questionnaire have asked?
We believe the Security Considerations section in the specification does a fairly decent job of describing the security issues we are trying to tackle and which one are out of scope.
