import React from 'react';
import { Link } from 'react-router-dom';
import Loading from '../../components/Loading';
import { useCollectionsTreeQuery } from './api'
import { useTranslation } from 'react-i18next';
import { TreeComponentProps, TreeView } from '../../components/TreeView';

function CollectionItem(props: TreeComponentProps) {
    return <Link to={"/notes/" + props.item.slug}>
        {
            (props.item.view === "NOTES") ? ("📝") :
            (props.item.view === "BOOKMARKS") ? ("🔗") :
            (props.item.view === "CHAT") ? ("💬") :
            ("📁")
        }
        {props.item.name}
    </Link>;
}

export default function CollectionsTree() {
    const { t } = useTranslation("common");
    const treeData = useCollectionsTreeQuery(0);

    if (treeData.loading) {
        return <Loading/>;
    } else if (treeData.error) {
        return <span style={{color: "red"}}>{treeData.error.message}</span>;
    } else {
        const pagesResult = treeData.data.notesCollectionsListBySlug;
        const items = pagesResult.items;
        if (items.length === 0) {
            return <div>{t("notes.collections.empty")}</div>;
        } else {
            return <TreeView
                items={items}
                component={CollectionItem}
                collapsible={true}
            />;
        }
    }
};