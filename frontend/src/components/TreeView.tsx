import React from "react";

export interface TreeItem {
    id: any;
    children: TreeItem[];
}

export interface TreeComponentProps<T = TreeItem|any> {
    item: T;
}

export interface CollapseProps {
    collapsed: boolean;
    collapsible: boolean;
    toggleCollapsed: () => void;
}

function DefaultCollapseComponent(props: CollapseProps) {
    function toggleCollapsed(e: React.MouseEvent<HTMLButtonElement>) {
        e.preventDefault();
        props.toggleCollapsed();
    }

    return <span
        style={{
            marginRight: props.collapsible ? undefined : "10px",
            borderLeft: "1px solid black",
            height: "100%",
        }}
    >
        {
            props.collapsible &&
            <button onClick={toggleCollapsed}>{props.collapsed ? ">" : "V"}</button>
        }
    </span>;
}

interface TreeNodeProps {
    item: TreeItem,
    component: React.ComponentType<any>;
    collapsible: boolean;
    collapseComponent: React.ComponentType<any>|null;
    collapsedItems: TreeItem[];
    setItemCollapsed: (item: TreeItem, collapsed: boolean) => void;
}

function TreeNode(props: TreeNodeProps) {
    const CollapseComponent = props.collapseComponent || DefaultCollapseComponent;
    const collapsed = props.collapsedItems.includes(props.item);
    const hasChildren = props.item.children && props.item.children.length > 0;
    return <span>
        <CollapseComponent
            collapsed={collapsed}
            collapsible={hasChildren && props.collapsible}
            toggleCollapsed={() => props.setItemCollapsed(props.item, !collapsed)}
        />
        <props.component item={props.item}/>
        {
            hasChildren && props.item.children.map((child: any) => {
                return <TreeNode
                    key={child.id}
                    item={child}
                    component={props.component}
                    collapsible={props.collapsible}
                    collapseComponent={props.collapseComponent}
                    collapsedItems={props.collapsedItems}
                    setItemCollapsed={props.setItemCollapsed}
                />;
            })
        }
    </span>;
}

interface TreeViewProps {
    items: TreeItem[];
    component: React.ComponentType<any>;
    collapsible?: boolean;
    collapseComponent?: React.ComponentType<any>;
};

export function TreeView(props: TreeViewProps) {
    const [collapsedItems, setCollapsedItems] = React.useState<TreeItem[]>([]);

    function setItemCollapsed(item: TreeItem, collapsed: boolean) {
        if (collapsed) {
            setCollapsedItems([...collapsedItems, item]);
        } else {
            setCollapsedItems(collapsedItems.filter((i) => i !== item));
        }
    }

    return <div>
        {
            props.items.map((item: any) => {
                return <TreeNode
                    key={item.id}
                    item={item}
                    component={props.component}
                    collapsible={props.collapsible || false}
                    collapseComponent={props.collapseComponent || null}
                    collapsedItems={collapsedItems}
                    setItemCollapsed={setItemCollapsed}
                />;
            })
        }
    </div>;
}
