from typing import TYPE_CHECKING, Any, Dict, Optional, Sequence, Type

from sqlalchemy.engine.result import Row

from edgy.core.db.models.base import EdgyBaseModel

if TYPE_CHECKING:  # pragma: no cover
    from edgy import Model


class ModelRow(EdgyBaseModel):
    """
    Builds a row for a specific model
    """

    @classmethod
    def from_sqla_row(
        cls,
        row: Row,
        select_related: Sequence[Any],
    ) -> Optional[Type["Model"]]:
        """
        Class method to convert a SQLAlchemy Row result into a EdgyModel row type.
        """
        item: Dict[str, Any] = {}
        select_related = select_related or []

        for related in select_related:
            if "__" in related:
                first_part, remainder = related.split("__", 1)
                try:
                    model_cls = cls.fields[first_part].target
                except KeyError:
                    model_cls = getattr(cls, first_part).related_from
                item[first_part] = model_cls.from_sqla_row(row, select_related=[remainder])
            else:
                try:
                    model_cls = cls.fields[related].target
                except KeyError:
                    model_cls = getattr(cls, related).related_from
                item[related] = model_cls.from_sqla_row(row)

        # Pull out the regular column values.
        for column in cls.table.columns:
            # Making sure when a table is reflected, maps the right fields of the ReflectModel
            if column.name not in cls.fields.keys():
                continue

            elif column.name not in item:
                item[column.name] = row[column]

        if cls.meta.related_names:
            item = cls.populate_nested_models_from_row(item, row)

        return cls(**item)

    @classmethod
    def populate_nested_models_from_row(cls, item: Dict[str, Any], row: Row) -> Dict[Any, Any]:
        """
        Populates the database model with the nested results from the row.
        """
        for related in cls.meta.related_names:
            ...
