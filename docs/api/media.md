---
icon: lucide/image-up
---

# Media

## Uploading a file

```http
POST /media/ HTTP/1.1
Content-Type: multipart/form-data
```

The body is a multipart form with a single `file` part, plus an optional
`visibility` field (`"public"`, the default, or `"private"`). It requires
the `add` permission on the media model. Unlike every other endpoint, this
one doesn't accept JSON.

The file's type is detected from its bytes, never from the
`Content-Type` the client declared for the part, so renaming a script to
`photo.png` doesn't get it through. By default, PNG, JPEG, WebP, and PDF
are accepted; anything else is rejected with a `400`, with the reason under
`files.file`. Images are also checked for integrity and for decompression
bombs, and their dimensions are recorded as `width` and `height`.

Files over `MEDIA_MAX_BYTES` (5 MiB by default) are rejected with a `413`
before they're read into memory.

The file is stored in Bunny Storage first and recorded afterward. If
recording fails, the stored file is deleted again, so storage never fills
with files no row points to. If Bunny itself fails, the request ends in a
`500` and nothing is recorded.

## Reading files

```http
GET /media/ HTTP/1.1
```

```http
GET /media/{id}/ HTTP/1.1
```

The collection is paginated, filterable by `visibility` and
`uploaded_by_id`, and orderable by `created_at` and `size`. Files are
never deleted: other tables can keep referring to them indefinitely.

Responses carry a `url` for the file, never its storage key:

- **Public** files resolve to a stable URL on `BUNNY_PULL_ZONE_HOST`.
- **Private** files resolve to a signed URL on
  `BUNNY_PRIVATE_PULL_ZONE_HOST`, valid for `BUNNY_SIGNED_URL_TTL_SECONDS`
  (5 minutes by default). It uses Bunny's token authentication, so fetch
  the record again for a fresh link instead of storing the URL.

## Configuring Bunny

| Variable                       | Purpose                                                       |
| ------------------------------ | ------------------------------------------------------------- |
| `BUNNY_STORAGE_ZONE`           | Storage zone that holds every file.                           |
| `BUNNY_STORAGE_HOST`           | Regional storage endpoint, `storage.bunnycdn.com` by default. |
| `BUNNY_STORAGE_API_KEY`        | The storage zone's password.                                  |
| `BUNNY_PULL_ZONE_HOST`         | Hostname of the pull zone serving public files.               |
| `BUNNY_PRIVATE_PULL_ZONE_HOST` | Hostname of the pull zone serving private files.              |
| `BUNNY_TOKEN_AUTH_KEY`         | Token authentication key of the private pull zone.            |
| `BUNNY_SIGNED_URL_TTL_SECONDS` | How long signed URLs stay valid.                              |
| `MEDIA_ALLOWED_MIME`           | JSON list of accepted types.                                  |
| `MEDIA_MAX_BYTES`              | Maximum file size.                                            |

Both pull zones front the same storage zone, and files are stored under a
`public/` or `private/` prefix that the database keeps in sync with each
row's visibility. Enable token authentication on the private pull zone,
and restrict the public pull zone to the `public/` prefix (with an edge
rule) so private files can't be fetched unsigned through it.
