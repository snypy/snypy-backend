# Snippet export / import

**Status: Draft.** This document specifies the API contract and file format for exporting
and importing snippets ([#235](https://github.com/snypy/snypy-backend/issues/235)). Nothing
described here is implemented yet; implementation is tracked in
[#124](https://github.com/snypy/snypy-backend/issues/124). Items marked **(proposed)** depend
on the [open decisions](#open-decisions) and are not approved yet.

Files:

- [`export-import/export.schema.json`](export-import/export.schema.json): JSON Schema (draft 2020-12) of the export file, version 1
- [`export-import/examples/export.json`](export-import/examples/export.json): example export, also a valid import body
- [`export-import/examples/export-empty.json`](export-import/examples/export-empty.json): export of an empty result
- [`export-import/examples/import-response-201.json`](export-import/examples/import-response-201.json): import success response for `export.json`
- [`export-import/examples/import-response-400.json`](export-import/examples/import-response-400.json): validation error response
- [`export-import/examples/import-response-400-version.json`](export-import/examples/import-response-400-version.json): unsupported version response

## Goals

- Export the snippets matching the current snippet-list filter, with their files and labels, as one JSON file.
- Import such a file into the personal scope or into a team, on the same or another SnyPy instance.
- Every imported snippet and label belongs to the importing user (`Snippet.user` / `Label.user` are
  `UserForeignKey(auto_user_add=True)`).

## File format (version 1)

```json
{
  "format": "snypy-export",
  "version": 1,
  "exportedAt": "2026-09-27T16:00:00Z",
  "source": "https://api.snypy.com",
  "labels": [{ "key": "l1", "name": "django" }],
  "snippets": [
    {
      "title": "Read-only DRF viewset",
      "description": "",
      "visibility": "PUBLIC",
      "labels": ["l1"],
      "files": [{ "name": "viewsets.py", "language": "python", "content": "..." }]
    }
  ]
}
```

| Field | Type | Required | Maps to / rule |
| --- | --- | --- | --- |
| `format` | string | yes | Always `"snypy-export"` |
| `version` | integer | yes | `1` |
| `exportedAt` | string (RFC 3339) | no | Informational, ignored on import |
| `source` | string | no | Informational, ignored on import |
| `labels[]` | array | yes (may be empty) | Labels referenced by the exported snippets |
| `labels[].key` | string, non-empty | yes | File-local reference, unique within `labels[]`. Not a database id |
| `labels[].name` | string, 1-255 chars | yes | `Label.name` (`max_length=255`) |
| `snippets[]` | array | yes (may be empty) | |
| `snippets[].title` | string, 1-255 chars | yes | `Snippet.title` (`max_length=255`, not blank) |
| `snippets[].description` | string | no, default `""` | `Snippet.description` (blank allowed) |
| `snippets[].visibility` | `"PUBLIC"` \| `"PRIVATE"` | yes | `Snippet.visibility` choices |
| `snippets[].labels[]` | array of label keys | no, default `[]` | One `SnippetLabel` per resolved key |
| `snippets[].files[]` | array | yes (may be empty) | `File` rows of the snippet |
| `files[].name` | string, 1-255 chars | yes | `File.name` (`max_length=255`, not blank) |
| `files[].language` | string, 1-255 chars | yes | `Language.name`, matched case-insensitively |
| `files[].content` | string | yes (may be `""`) | `File.content` (blank allowed) |

The file contains **no database ids and no user or team ids**. Labels are referenced by file-local
`key`, languages by name. Unknown properties are ignored on import, so later minor additions do
not break older importers; incompatible changes bump `version`.

Not exported (proposed, decision 5): database ids, user and team identities, timestamps
(`created_date` / `modified_date`), favorites (`SnippetFavorite` is per-user state), `Extension`
rows (instance-level reference data) and shares. The `shares` app currently has no models
(`snypy/shares/models.py` is empty), so there is nothing to export; if shares are added later
they reference users of the source instance and cannot be carried across instances.

The schema cannot express every rule. In addition to the schema, an import checks:
`labels[].key` values are unique, every `snippets[].labels[]` entry resolves to a key, and the
size limits below.

## Endpoints

Both endpoints are extra actions on `SnippetViewSet` (router prefix `snippet`), so they sit under
`/api/v1/snippet/` and use the existing authentication (token or session) and
`BaseModelPermissions`. They are annotated with `drf_spectacular.utils.extend_schema`, with
dedicated request/response serializers, so the generated REST client gets typed methods.

### `GET /api/v1/snippet/export/` (proposed, decision 2)

`@action(detail=False, methods=["GET"])`. Requires authentication and the `snippets.view_snippet`
permission (the `GET` entry of `BaseModelPermissions.perms_map`).

Query parameters: the same as `GET /api/v1/snippet/` (`SnippetFilter` + `SearchFilter`):

| Param | Meaning |
| --- | --- |
| `search` | Substring search in `title`, `description` |
| `labels` | Label id (repeatable) |
| `visibility` | `PUBLIC` / `PRIVATE` |
| `files__language` | Language id |
| `user` | User id |
| `team` | Team id |
| `team_is_null` | `true` = personal snippets only |
| `favorite` | Favorited by the requesting user |
| `labeled` | Has at least one label |

Response `200 OK`, `Content-Type: application/json`,
`Content-Disposition: attachment; filename="snypy-export-<YYYY-MM-DD>.json"`, body = export file.
An empty result is still `200` with empty arrays (see `examples/export-empty.json`).

Status codes: `200`, `400` (invalid filter value), `401` (not authenticated), `403` (missing
`view_snippet` permission).

### `POST /api/v1/snippet/import/` (proposed, decision 2)

`@action(detail=False, methods=["POST"])`. Requires authentication and the `snippets.add_snippet`
permission (the `POST` entry of `perms_map`).

Request, one of:

- `Content-Type: application/json`: body is the export file; target team as query parameter `?team=<id>`.
- `Content-Type: multipart/form-data`: field `file` (the export file), optional field `team`.

| Param | Type | Required | Meaning |
| --- | --- | --- | --- |
| `team` | integer | no | Target team id. Omitted = personal scope (`team=None`) |

Response `201 Created` (see `examples/import-response-201.json`):

```json
{
  "snippets": 3,
  "files": 4,
  "labels": { "created": 1, "reused": 2 },
  "warnings": [{ "path": "snippets[2].files[0].language", "message": "Unknown language 'zig', imported as 'text'." }]
}
```

Error response `400 Bad Request` (see `examples/import-response-400.json`):

```json
{ "errors": [{ "path": "snippets[1].labels[0]", "message": "Unknown label key 'l9'." }] }
```

`path` is a JSON path into the uploaded document (`snippets[3].files[0].name`), `version`,
`team`, `file` or `""` for the document as a whole. All errors found are reported, not only the
first. Note: this shape differs from DRF's default field-keyed `ValidationError` body; the view
converts nested serializer errors into the flat list.

| Status | When |
| --- | --- |
| `201` | Import committed (also for an empty file; counts are `0`) |
| `400` | Not JSON, schema/validation error, unsupported `format`/`version`, invalid or not permitted `team`, too many snippets |
| `401` | Not authenticated |
| `403` | Missing `snippets.add_snippet` permission |
| `413` | Request body over the size limit (proposed, decision 7) |

## Import validation

1. Parse the body (JSON or the multipart `file`). Not valid JSON or not an object: `400`, path `""` / `file`.
2. `format` must equal `"snypy-export"`; `version` must be a supported version (only `1`). Otherwise
   `400` with path `format` / `version`; nothing else is validated.
3. Validate the document against the version's schema: required fields, types, `visibility`
   choices, lengths (`title`, `files[].name`, `labels[].name`, `files[].language` at most 255
   characters, `title`, `name`, `language`, `key` not blank).
4. Cross-references: `labels[].key` unique (duplicate key: error at `labels[i].key`); every
   `snippets[i].labels[j]` resolves to a key (error at that path). A key repeated within one
   snippet is applied once.
5. Size limit (proposed, decision 7): request body at most 10 MB, at most 5000 snippets.
6. Target team check (see [Permissions](#permissions)).
7. Resolve languages (decision 3) and labels (decision 4), then create everything inside one
   `transaction.atomic()` block. Any error means nothing is imported and the response is `400`.

**Languages (proposed, decision 3).** `files[].language` is matched against `Language.name`
case-insensitively. `Language.name` is not unique in the model; with several matches the lowest
id wins. An unknown language falls back to the instance's plain-text language and adds a
warning. The shipped fixture (`snypy/fixtures/languages.json`) names it `text` (lower case, like
all fixture languages: `python`, `sh`, `json`, ...). If no plain-text language exists, the
unknown language is a `400` error at that path.

**Labels (proposed, decision 4).** Labels are de-duplicated by name, case-insensitively, first
within the file (two keys with the same name map to one label) and then against the target scope:

- personal import: existing labels with `user = importer` and `team = None`;
- team import: existing labels with `team = <team>`.

A matching label is reused (`labels.reused`), otherwise a new label is created in the target scope
(`labels.created`). `Label.name` is not unique in the model; with several matches the lowest id
wins. Labels listed in `labels[]` but used by no snippet are still resolved/created.

## Permissions

**Export (proposed, decision 1)** includes the snippets that match the filter **and** are either
owned by the requesting user or belong to a team the user is a member of (any role:
`EDITOR`, `CONTRIBUTOR`, `SUBSCRIBER`). Public snippets of other users are excluded even though
`Snippet.objects.viewable()` returns them. For each exported snippet, all its files and the names
of all labels attached to it are exported.

**Import into a team.** Today a snippet may be created in a team by users with role `CONTRIBUTOR`
or `EDITOR` in that team (`SnippetSerializer.validate_team`, `snypy/snippets/rest/serializers.py`,
lines 102-112); `SUBSCRIBER` may not. Import follows the same rule (decision 6). Not a member, a
`SUBSCRIBER`, or a non-existent team id: `400` with path `team` (same as snippet create, which does
not reveal whether the team exists).

Note that only `EDITOR` may later edit or delete team snippets (`SnippetQuerySet.editable`,
`snypy/snippets/models/querysets.py`, lines 37-53); a `CONTRIBUTOR` can import into a team but not
modify what was imported, which matches the existing create/edit split.

**Ownership.** Imported snippets and labels always get `user = importer`; the file carries no
owner information. `team` is the `team` parameter or `None`.

## Edge cases

| Case | Behaviour |
| --- | --- |
| Same file imported twice | Snippets are created again (no duplicate detection in v1). Labels are reused by name, so they are not duplicated |
| Duplicate snippets inside one file | Imported as separate snippets |
| Two label entries with the same name (different keys) | Collapsed to one label |
| Duplicate `labels[].key` | `400` at `labels[i].key` |
| Snippet references an unknown label key | `400` at `snippets[i].labels[j]` |
| Same key twice in one snippet | Applied once |
| Label in `labels[]` not used by any snippet | Resolved/created anyway |
| Duplicate file names within one snippet | Allowed (no constraint on `File.name`) |
| Snippet with `files: []` | Allowed (the model and snippet API allow snippets without files) |
| Unknown language | Plain-text fallback with warning, or `400` if the instance has no `text` language (decision 3) |
| Snippet owned by another user / another team | Only reachable on export via team membership; on import ownership is always the importer |
| Team scope on export | Team snippets are exported without their team; import target is chosen per request |
| Team import as `SUBSCRIBER` or non-member | `400` at `team` |
| Unsupported `format` or `version` | `400` at `format` / `version`, see `examples/import-response-400-version.json` |
| Empty export (no matching snippets) | `200` with `labels: []`, `snippets: []` |
| Empty import | `201` with all counts `0` |
| Body over the size limit / more than 5000 snippets | `413` / `400` (decision 7) |
| Error in any snippet | Whole import rolled back |

## Open decisions

These need maintainer confirmation before #124 is implemented.

1. **Export scope.** Proposed: filter ∩ (own snippets + snippets of the user's teams). Alternative:
   everything `viewable()`, including other users' public snippets.
2. **Endpoint shape.** Proposed: `GET /api/v1/snippet/export/` and `POST /api/v1/snippet/import/`
   as `SnippetViewSet` actions, JSON or multipart request for import.
3. **Unknown languages.** Proposed: case-insensitive name match, fallback to `text` with a warning.
   Alternative: reject the import.
4. **Labels.** Proposed: reuse an existing label with the same name (case-insensitive) in the target
   scope, otherwise create.
5. **Excluded data.** Proposed: visibility kept; favorites, shares, timestamps, user/team identities
   and ids not exported.
6. **Team import permission.** Proposed: `EDITOR` or `CONTRIBUTOR`, matching the existing
   team-snippet create rule (verified in code, see [Permissions](#permissions)).
7. **Size limit.** Proposed: 10 MB request body, 5000 snippets. Django's default
   `DATA_UPLOAD_MAX_MEMORY_SIZE` is 2.5 MB and applies to non-file request bodies, so a 10 MB JSON
   body needs that setting raised (or the import restricted to multipart uploads). A reverse proxy
   in front of the API may impose its own limit.
8. **Field naming.** The draft uses camelCase for `exportedAt`; the rest of the REST API uses
   snake_case (`created_date`). Keep or rename to `exported_at` before version 1 is frozen.

## Later (not in version 1)

- Exporting/importing team membership or whole teams.
- Duplicate detection for idempotent re-imports.
