from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class CreateTopicRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    description: str | None = None
    parent_id: UUID | None = None


class UpdateTopicRequest(BaseModel):
    """Partial topic update payload.

    Fields omitted from the request are left unchanged.

    `name` and `slug` are optional in the schema so they may be omitted,
    but they cannot be explicitly set to null.
    `description` may be null because clearing an existing description
     is a valid update.
    """

    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None

    @model_validator(mode="after")
    def validate_update_fields(self) -> "UpdateTopicRequest":
        """
        Reject explicit nulls for non-nullable update fields.

        `model_fields_set` is used to distinguish a field that was omitted
        from the request from a field that was explicitly sent as null.

        For example:
            {}              -> `name` was not provided -> leave it unchanged
            {"name": null}  -> `name` was explicitly provided as null -> reject it

        Without checking `model_fields_set`, both cases would result in
        `self.name is None` and could not be distinguished.
        """
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")

        if "name" in self.model_fields_set and self.name is None:
            raise ValueError("name cannot be null")

        if "slug" in self.model_fields_set and self.slug is None:
            raise ValueError("slug cannot be null")

        return self
