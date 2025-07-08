# Dev Notes - Ongoing

- [ ] Check for switching from raw `Depends` to `Query` for query params
- [ ] Review ownership validation for update/create/delete/upsert method.
  Currently, there is no mechanism to check that the `resources_id` (`transaction_id`, `categorty_id`, etc.) is owned by the current user identified by `user_id`. It should also match the `account_id` (same ownership issue).

  **Update**: check if the resource given the `resource_id` is owned by the user given the `user_id`.

  **Create**: check if the account given the `account_id` is owned by the user given the `user_id`.

  **Delete**: check if the resource given the  `resource_id` is owned by the user given the `user_id`.
