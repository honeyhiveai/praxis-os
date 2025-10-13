import React from 'react';
import Content from '@theme-original/DocItem/Content';
import type ContentType from '@theme/DocItem/Content';
import type {WrapperProps} from '@docusaurus/types';
import {useDoc} from '@docusaurus/plugin-content-docs/client';
import DocTypeBadge, {type DocType} from '@site/src/components/DocTypeBadge';

type Props = WrapperProps<typeof ContentType>;

export default function ContentWrapper(props: Props): JSX.Element {
  const {frontMatter} = useDoc();
  const docType = frontMatter.doc_type as DocType | undefined;

  return (
    <>
      {docType && <DocTypeBadge type={docType} />}
      <Content {...props} />
    </>
  );
}

