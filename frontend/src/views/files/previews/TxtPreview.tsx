import React from 'react';
import axios from 'axios';
import Loading from '../../../components/Loading';
import { PreviewProps, Preview, primaryMimeType } from './preview';

function TxtPreview(props: PreviewProps) {
    const [contents, setContents] = React.useState<string|undefined>(undefined);
    React.useEffect(() => {
        if (props.contentUrl === undefined) { return; }
        axios.get(props.contentUrl, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('authentication-token')}`
            },
        })
        .then(response => response.data)
        .then(text => setContents(text));
    }, [props.contentUrl]);

    return (
        (contents !== undefined) ? (
            <pre>{contents}</pre>
        ) : (
            <Loading/>
        )
    );
}

export default new Preview(primaryMimeType("text"), TxtPreview, true);
