# sphinx-theme-builder's tests

We're using tests at 4 levels:

- "unit" -- check behaviour of one function/method at a time.
  - no mocking.
- "integration" -- check that units exchange information correctly.
  - mocking allowed.
- "system" -- check that the entire pipeline passes information correctly.
  - no mocking.
- "workflow" -- check that specific end-user behaviours are correct.
  - no mocking.
