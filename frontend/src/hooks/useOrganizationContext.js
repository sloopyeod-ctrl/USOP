import {
  useContext,
} from "react";

import OrganizationContext from
  "../context/ActiveOrganizationContext";


export default function useOrganizationContext() {
  const context = useContext(
    OrganizationContext,
  );

  if (!context) {
    throw new Error(
      "useOrganizationContext must be used "
      + "within an OrganizationProvider.",
    );
  }

  return context;
}